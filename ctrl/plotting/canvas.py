# ctrl/plotting/canvas.py
from __future__ import annotations

from typing import Optional, List, Tuple
import numpy as np

from PySide6 import QtCore
from PySide6.QtCore import Slot
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from ..ui_config import UIConfig
from .toolbar import PVToolbar  # apenas para manter coesão do módulo (usado na View)


# =============================================================================
# Mpl Canvas (View pura de plotagem: cursores V/H, Kp e overlays)
# =============================================================================
class MplCanvas(FigureCanvas):
    def __init__(self, parent=None):
        fig = Figure(figsize=(7, 4), constrained_layout=False)
        fig.subplots_adjust(
            left=UIConfig.LEFT_MARGIN, right=UIConfig.RIGHT_MARGIN, bottom=0.12, top=0.95
        )
        self.fig = fig
        self.ax_y = fig.add_subplot(111)       # eixo principal (y) à ESQUERDA
        super().__init__(fig)
        self.setParent(parent)

        # Segundo eixo (u) como twin — mantém na DIREITA (padrão)
        self.ax_u = self.ax_y.twinx()

        # Estética & pads
        self.ax_y.tick_params(axis='y', pad=UIConfig.TICK_PAD, labelsize=9, colors='C0')
        self.ax_u.tick_params(axis='y', pad=UIConfig.TICK_PAD, labelsize=9, colors='C1')
        self.ax_y.tick_params(axis='x', labelsize=9)
        self.ax_y.set_ylabel("PV (y)", labelpad=UIConfig.LABELPAD, color='C0')
        self.ax_u.set_ylabel("Entrada (u)", labelpad=UIConfig.LABELPAD, color='C1')
        self.ax_y.set_xlabel("Tempo (s)")
        self.ax_y.grid(True, alpha=0.25)

        (self.line_y,) = self.ax_y.plot([], [], color='C0', label="PV (y)")
        (self.line_u,) = self.ax_u.plot([], [], color='C1', label="Entrada (u)")

        # Legenda combinada
        lines = [self.line_y, self.line_u]
        labels = [ln.get_label() for ln in lines]
        self.ax_y.legend(lines, labels, loc="upper right")

        # Cursor leve (cruz)
        self.hline = self.ax_y.axhline(0, lw=0.8, ls="--", alpha=0.4, visible=False)
        self.vline = self.ax_y.axvline(0, lw=0.8, ls="--", alpha=0.4, visible=False)

        self.mpl_connect("motion_notify_event", self._on_move)
        self.mpl_connect("axes_leave_event", self._on_leave)
        self.mpl_connect("button_press_event", self._on_click)
        self.mpl_connect("button_release_event", self._on_release)
        self.mpl_connect("key_press_event", self._on_key)

        # Marcador fixo legado
        self.lock_vline = None
        self.annot = self.ax_y.annotate(
            "", xy=(0, 0), xytext=(10, 10), textcoords="offset points",
            bbox=dict(boxstyle="round", fc="w", ec="0.5", alpha=0.9),
            arrowprops=dict(arrowstyle="->")
        )
        self.annot.set_visible(False)

        # Cursores V/H
        self.cursor_mode: Optional[str] = None      # None | 'v' | 'h'
        self.cursor_points: List[Tuple[float, float]] = []  # cliques
        self.cursor_artists: List = []
        self.cursor_text_box_v = self.ax_y.text(
            0.01, 0.98, "", transform=self.ax_y.transAxes, va='top', ha='left',
            bbox=dict(boxstyle="round", fc="w", ec="0.5", alpha=0.9), fontsize=9, visible=False, zorder=5
        )
        self.cursor_text_box_h = self.ax_y.text(
            0.01, 0.02, "", transform=self.ax_y.transAxes, va='bottom', ha='left',
            bbox=dict(boxstyle="round", fc="w", ec="0.5", alpha=0.9), fontsize=9, visible=False, zorder=5
        )

        # Kp (hipotenusa)
        self.kp_mode: bool = False
        self.kp_points: List[Tuple[float, float]] = []   # (x,y) em eixo y
        self.kp_line = None
        self.kp_text_box = self.ax_y.text(
            0.99, 0.02, "", transform=self.ax_y.transAxes, va='bottom', ha='right',
            bbox=dict(boxstyle="round", fc="w", ec="0.5", alpha=0.9), fontsize=9, visible=False
        )
        # Estados de edição/colocação
        self.kp_edit_idx: Optional[int] = None       # 0/1 durante edição; None caso contrário
        self.kp_creating: bool = False               # True após 1º clique quando não existe Kp
        self.kp_backup_points: Optional[List[Tuple[float,float]]] = None

        self.overlays = []

    # ---------- utilitários de mapeamento ----------
    def _to_ax_y_ydata(self, ev):
        """y (em dados do eixo esquerdo) a partir do evento, esteja o mouse sobre ax_y ou ax_u."""
        try:
            if ev.ydata is not None and ev.inaxes is self.ax_y:
                return float(ev.ydata)
            if ev.ydata is not None and ev.inaxes is self.ax_u:
                _, py = self.ax_u.transData.transform((0.0, float(ev.ydata)))
                return float(self.ax_y.transData.inverted().transform((0.0, py))[1])
            return float(self.ax_y.transData.inverted().transform((ev.x, ev.y))[1])
        except Exception:
            return None

    def _u_to_ydata(self, x: float, uval: float) -> float:
        """Mapear valor do eixo direito (u) no tempo x para a coordenada em y (eixo esquerdo) mantendo a altura em pixels."""
        xp, yp = self.ax_u.transData.transform((float(x), float(uval)))
        return float(self.ax_y.transData.inverted().transform((xp, yp))[1])

    # ---------- handlers do mouse/teclado ----------
    def _on_move(self, ev):
        if not ev.inaxes or ev.inaxes not in (self.ax_y, self.ax_u):
            self.hline.set_visible(False); self.vline.set_visible(False); self.draw_idle(); return

        # Cursor leve
        self.hline.set_visible(True); self.vline.set_visible(True)
        y_left = self._to_ax_y_ydata(ev)
        if y_left is not None:
            self.hline.set_ydata([y_left])
        self.vline.set_xdata([ev.xdata])

        # Kp: mover sem segurar (edição ou colocação)
        if self.kp_mode and ev.xdata is not None:
            if self.kp_edit_idx is not None and len(self.kp_points) == 2:
                # Editando endpoint existente
                self._kp_update_point(self.kp_edit_idx, ev.xdata, live=True, ev_pixels=(ev.x, ev.y))
                if self.kp_line is not None:
                    self.kp_line.set_linestyle('--')
            elif self.kp_creating and len(self.kp_points) >= 1:
                # Colocando P2 provisório
                xq = float(ev.xdata)
                tx = np.asarray(self.line_y.get_xdata(), dtype=float)
                yy = np.asarray(self.line_y.get_ydata(), dtype=float)
                y_guess = self._interp_at(xq, tx, yy)
                if np.isfinite(y_guess):
                    x_final, y_final = self._kp_snap_point(xq, y_guess, ev_pixels=(ev.x, ev.y))
                    if len(self.kp_points) == 1:
                        self.kp_points = [self.kp_points[0], (x_final, y_final)]
                    else:
                        self.kp_points[1] = (x_final, y_final)
                    self._kp_draw_line(linestyle='--')
                    self._kp_update_text()

        self.draw_idle()

    def _on_leave(self, _):
        self.hline.set_visible(False); self.vline.set_visible(False); self.draw_idle()

    def _on_click(self, ev):
        if not ev.inaxes or ev.inaxes not in (self.ax_y, self.ax_u):
            return

        if self.kp_mode:
            if ev.button == 3:
                self._kp_cancel_operation()
                return
            self._kp_click_flow(ev)
            return

        if self.cursor_mode in ('v', 'h'):
            self._handle_cursor_click(ev)
            return

        # Legado: travar vline
        if ev.button == 1:
            x = ev.xdata
            if self.lock_vline is None:
                self.lock_vline = self.ax_y.axvline(x, lw=1.1, ls="-.", alpha=0.7)
            else:
                self.lock_vline.set_xdata([x])
            self.annot.xy = (x, self.ax_y.get_ybound()[1])
            self.annot.set_visible(True)
            self.draw_idle()
        elif ev.button == 3:
            if self.lock_vline is not None:
                self.lock_vline.remove(); self.lock_vline = None
            self.annot.set_visible(False)
            self.draw_idle()

    def _on_release(self, ev):
        pass

    def _on_key(self, ev):
        if self.kp_mode and ev.key == 'escape':
            self._kp_cancel_operation()

    # -------------------- Cursores V/H --------------------
    def set_cursor_mode(self, mode: Optional[str]):
        self.cursor_mode = mode
        self.cursor_points.clear()
        self.draw_idle()

    def clear_cursors(self):
        for a in self.cursor_artists:
            try:
                a.remove()
            except Exception:
                pass
        self.cursor_artists.clear()
        self.cursor_points.clear()
        self.cursor_text_box_v.set_visible(False)
        self.cursor_text_box_h.set_visible(False)
        self.kp_clear()
        self.draw_idle()

    def _handle_cursor_click(self, ev):
        if ev.xdata is None:
            return
        x = float(ev.xdata)
        if self.cursor_mode == 'h':
            y_left = self._to_ax_y_ydata(ev)
            if y_left is None:
                return
            self.cursor_points.append((x, float(y_left)))
            ln = self.ax_y.axhline(y_left, lw=1.2, ls="--", alpha=0.8, color='k')
            self.cursor_artists.append(ln)
        elif self.cursor_mode == 'v':
            self.cursor_points.append((x, float(ev.ydata if ev.ydata is not None else 0.0)))
            ln = self.ax_y.axvline(x, lw=1.2, ls="--", alpha=0.8, color='k')
            self.cursor_artists.append(ln)
        self.draw_idle()

        if len(self.cursor_points) >= 2:
            p1, p2 = self.cursor_points[-2], self.cursor_points[-1]
            if self.cursor_mode == 'v':
                self._calc_vertical_cursors(p1, p2)
            elif self.cursor_mode == 'h':
                self._calc_horizontal_cursors(p1, p2)

    @staticmethod
    def _interp_at(xq: float, x: np.ndarray, y: np.ndarray) -> float:
        if len(x) < 2 or not np.isfinite(xq):
            return float('nan')
        x = np.asarray(x); y = np.asarray(y)
        return float(np.interp(xq, x, y))

    def _calc_vertical_cursors(self, p1: Tuple[float, float], p2: Tuple[float, float]):
        x1, _ = p1; x2, _ = p2
        if x2 < x1:
            x1, x2 = x2, x1
        dt = x2 - x1
        l1 = self.ax_y.axvline(x1, lw=1.4, ls="-.", alpha=0.9, color='k')
        l2 = self.ax_y.axvline(x2, lw=1.4, ls="-.", alpha=0.9, color='k')
        self.cursor_artists += [l1, l2]
        txt = f"V: x1={x1:.4g}s  x2={x2:.4g}s  Δt={dt:.4g}s"
        self.cursor_text_box_v.set_text(txt)
        self.cursor_text_box_v.set_visible(True)
        self.draw_idle()

    def _calc_horizontal_cursors(self, p1: Tuple[float, float], p2: Tuple[float, float]):
        x1, y1 = p1; x2, y2 = p2
        tx = np.asarray(self.line_y.get_xdata(), dtype=float)
        uu = np.asarray(self.line_u.get_ydata(), dtype=float)
        u1 = self._interp_at(x1, tx, uu)
        u2 = self._interp_at(x2, tx, uu)
        dy = abs(y2 - y1)
        du = abs(u2 - u1)
        lh1 = self.ax_y.axhline(y1, lw=1.4, ls="-.", alpha=0.9, color='k')
        lh2 = self.ax_y.axhline(y2, lw=1.4, ls="-.", alpha=0.9, color='k')
        self.cursor_artists += [lh1, lh2]
        txt = f"H: y1={y1:.4g}  y2={y2:.4g}  |Δy|={dy:.4g}   |Δu|={du:.4g}"
        self.cursor_text_box_h.set_text(txt)
        self.cursor_text_box_h.set_visible(True)
        self.draw_idle()

    # -------------------- Kp (hipotenusa) --------------------
    def set_kp_mode(self, enabled: bool):
        self.kp_mode = bool(enabled)
        if enabled:
            self.kp_edit_idx = None
            self.kp_creating = False
            self.kp_backup_points = None
            # Auto-colocação se não existir Kp ainda
            if not self.kp_points and self.kp_line is None:
                try:
                    self._kp_auto_place()
                except Exception:
                    pass
        self.draw_idle()

    def kp_clear(self):
        self.kp_points.clear()
        if self.kp_line is not None:
            try: self.kp_line.remove()
            except Exception: pass
            self.kp_line = None
        self.kp_text_box.set_visible(False)
        self.kp_edit_idx = None
        self.kp_creating = False
        self.kp_backup_points = None

    def _kp_click_flow(self, ev):
        xq = float(ev.xdata)
        # Caso 1: já existe Kp completo → tentar pegar endpoint próximo
        if len(self.kp_points) == 2 and self.kp_line is not None and not self.kp_creating and self.kp_edit_idx is None:
            idx = self._kp_pick_endpoint_by_click(ev, radius_px=12.0)
            if idx is None:
                return
            self.kp_edit_idx = idx
            self.kp_backup_points = list(self.kp_points)
            if self.kp_line is not None:
                self.kp_line.set_linestyle('--')
            return

        # Caso 2: estamos editando → segundo clique fixa
        if self.kp_edit_idx is not None:
            if self.kp_line is not None:
                self.kp_line.set_linestyle('-')
            self.kp_edit_idx = None
            self.kp_backup_points = None
            self._kp_update_text()
            self.draw_idle()
            return

        # Caso 3: não existe Kp ainda → iniciar colocação P1 manual (fallback, se auto-place não ocorreu)
        if len(self.kp_points) < 2 and self.kp_line is None and not self.kp_creating:
            tx = np.asarray(self.line_y.get_xdata(), dtype=float)
            yy = np.asarray(self.line_y.get_ydata(), dtype=float)
            y_guess = self._interp_at(xq, tx, yy)
            if not np.isfinite(y_guess):
                return
            x1, y1 = self._kp_snap_point(xq, y_guess, ev_pixels=(ev.x, ev.y))
            self.kp_points = [(x1, y1)]
            self.kp_creating = True
            (self.kp_line,) = self.ax_y.plot([x1, x1], [y1, y1], linestyle='--', color='k', lw=1.5, label='Kp')
            self.draw_idle()
            return

        # Caso 4: estamos criando e já temos P1 → segundo clique fixa P2
        if self.kp_creating and len(self.kp_points) == 2:
            if self.kp_line is not None:
                self.kp_line.set_linestyle('-')
            self.kp_creating = False
            self._kp_update_text()
            self.draw_idle()
            return

    def _kp_pick_endpoint_by_click(self, ev, radius_px: float) -> Optional[int]:
        if len(self.kp_points) != 2:
            return None
        x0, y0 = self.kp_points[0]
        x1, y1 = self.kp_points[1]
        p0 = self.ax_y.transData.transform((x0, y0))
        p1 = self.ax_y.transData.transform((x1, y1))
        click = np.array([ev.x, ev.y], dtype=float)
        d0 = np.linalg.norm(click - p0)
        d1 = np.linalg.norm(click - p1)
        if d0 <= radius_px or d1 <= radius_px:
            return 0 if d0 <= d1 else 1
        return None

    def _kp_cancel_operation(self):
        if self.kp_edit_idx is not None and self.kp_backup_points is not None:
            self.kp_points = list(self.kp_backup_points)
            self.kp_backup_points = None
            self.kp_edit_idx = None
            if self.kp_line is not None:
                (x0, y0), (x1, y1) = self.kp_points
                self.kp_line.set_data([x0, x1], [y0, y1])
                self.kp_line.set_linestyle('-')
            self._kp_update_text()
            self.draw_idle()
            return

        if self.kp_creating:
            self.kp_creating = False
            self.kp_points.clear()
            if self.kp_line is not None:
                try: self.kp_line.remove()
                except Exception: pass
                self.kp_line = None
            self.kp_text_box.set_visible(False)
            self.draw_idle()

    def _kp_update_point(self, idx: int, xnew: float, live: bool = True, ev_pixels=None):
        if len(self.kp_points) < 1:
            return
        tx = np.asarray(self.line_y.get_xdata(), dtype=float)
        yy = np.asarray(self.line_y.get_ydata(), dtype=float)
        if len(tx) < 2:
            return
        y_guess = self._interp_at(float(xnew), tx, yy)
        if not np.isfinite(y_guess):
            return
        x_final, y_final = self._kp_snap_point(float(xnew), float(y_guess), ev_pixels=ev_pixels)

        if len(self.kp_points) == 1:
            self.kp_points = [self.kp_points[0], (x_final, y_final)]
        else:
            pts = list(self.kp_points)
            pts[idx] = (x_final, y_final)
            self.kp_points = pts

        ls = '--' if live else '-'
        self._kp_draw_line(linestyle=ls)
        self._kp_update_text()

    def _kp_draw_line(self, linestyle='-'):
        if len(self.kp_points) < 1:
            return
        if self.kp_line is None:
            if len(self.kp_points) == 1:
                (x0, y0) = self.kp_points[0]
                (self.kp_line,) = self.ax_y.plot([x0, x0], [y0, y0], linestyle=linestyle, color='k', lw=1.5, label='Kp')
            else:
                (x0, y0), (x1, y1) = self.kp_points[:2]
                (self.kp_line,) = self.ax_y.plot([x0, x1], [y0, y1], linestyle=linestyle, color='k', lw=1.5, label='Kp')
        else:
            if len(self.kp_points) == 1:
                (x0, y0) = self.kp_points[0]
                self.kp_line.set_data([x0, x0], [y0, y0])
            else:
                (x0, y0), (x1, y1) = self.kp_points[:2]
                self.kp_line.set_data([x0, x1], [y0, y1])
            self.kp_line.set_linestyle(linestyle)
            self.kp_line.set_color('k')
            self.kp_line.set_linewidth(1.5)
        self.draw_idle()

    def _kp_update_text(self):
        if len(self.kp_points) != 2:
            self.kp_text_box.set_visible(False)
            return
        (x0, y0), (x1, y1) = self.kp_points[:2]
        dt = abs(x1 - x0)
        tx = np.asarray(self.line_y.get_xdata(), dtype=float)
        uu = np.asarray(self.line_u.get_ydata(), dtype=float)
        u0 = self._interp_at(x0, tx, uu)
        u1 = self._interp_at(x1, tx, uu)
        dy = abs(y1 - y0)
        du = abs(u1 - u0)
        txt = f"Kp  Δt={dt:.4g}s  |Δy|={dy:.4g}  |Δu|={du:.4g}"
        self.kp_text_box.set_text(txt)
        self.kp_text_box.set_visible(True)
        self.draw_idle()

    def _kp_snap_point(self, xq: float, y_guess: float, ev_pixels=None, radius_px: float = 12.0, win_frac: float = 0.05):
        if ev_pixels is None:
            px_ref, py_ref = self.ax_y.transData.transform((xq, y_guess))
        else:
            px_ref, py_ref = float(ev_pixels[0]), float(ev_pixels[1])

        xmin, xmax = self.ax_y.get_xbound()
        dx = max(1e-12, xmax - xmin)
        xwin = max(1e-9, win_frac * dx)

        tx = np.asarray(self.line_y.get_xdata(), dtype=float)
        if len(tx) < 2:
            return float(xq), float(y_guess)

        m = np.abs(tx - xq) <= xwin
        idxs = np.where(m)[0]
        if idxs.size == 0:
            return float(xq), float(y_guess)

        yy = np.asarray(self.line_y.get_ydata(), dtype=float)
        pts_y = np.column_stack([tx[idxs], yy[idxs]])
        pix_y = self.ax_y.transData.transform(pts_y)
        dists_y = np.hypot(pix_y[:,0] - px_ref, pix_y[:,1] - py_ref)
        best_y_dist = float(np.min(dists_y)) if dists_y.size else float('inf')
        best_y_idx = int(idxs[int(np.argmin(dists_y))]) if dists_y.size else None

        uu = np.asarray(self.line_u.get_ydata(), dtype=float)
        pts_u = np.column_stack([tx[idxs], uu[idxs]])
        pix_u = self.ax_u.transData.transform(pts_u)
        dists_u = np.hypot(pix_u[:,0] - px_ref, pix_u[:,1] - py_ref)
        best_u_dist = float(np.min(dists_u)) if dists_u.size else float('inf')
        best_u_idx = int(idxs[int(np.argmin(dists_u))]) if dists_u.size else None

        best_dist = min(best_y_dist, best_u_dist)
        if not np.isfinite(best_dist) or best_dist > radius_px:
            return float(xq), float(y_guess)

        if best_y_dist <= best_u_dist:
            x_fin = float(tx[best_y_idx]); y_fin = float(yy[best_y_idx])
            return x_fin, y_fin
        else:
            x_fin = float(tx[best_u_idx]); u_val = float(uu[best_u_idx])
            px, py = self.ax_u.transData.transform((x_fin, u_val))
            y_fin = float(self.ax_y.transData.inverted().transform((px, py))[1])
            return x_fin, y_fin
    # ---- helpers overlays ----
    def clear_overlays(self):
        for a in self.overlays:
            try:
                a.remove()
            except Exception:
                pass
        self.overlays.clear()
        self.draw_idle()

    def add_vline(self, x, **kw):
        a = self.ax_y.axvline(x, **kw); self.overlays.append(a); return a

    def add_hline(self, y, **kw):
        a = self.ax_y.axhline(y, **kw); self.overlays.append(a); return a

    def add_text(self, x, y, s, **kw):
        a = self.ax_y.text(x, y, s, **kw); self.overlays.append(a); return a
        
    # ---------- Auto-colocação inicial do Kp ao ativar (reta tangente) ----------
    def _kp_auto_place(self):
        tx = np.asarray(self.line_y.get_xdata(), dtype=float)
        yy = np.asarray(self.line_y.get_ydata(), dtype=float)
        uu_r = np.asarray(self.line_u.get_ydata(), dtype=float)
        if tx.size < 8 or yy.size != tx.size or uu_r.size != tx.size:
            return

        # 1) Derivada e início robusto
        try:
            dydt = np.gradient(yy, tx)
        except Exception:
            return
        absd = np.abs(dydt)
        max_s = float(np.max(absd)) if absd.size else 0.0
        if not np.isfinite(max_s) or max_s <= 0.0:
            return
        thr = 0.10 * max_s
        sel = absd >= thr
        if not np.any(sel):
            return
        sign_mean = np.sign(np.mean(dydt[sel])); sign_mean = 1.0 if sign_mean >= 0 else -1.0
        m_consec = 3
        i0 = None
        for k in range(0, tx.size - m_consec):
            window = dydt[k:k+m_consec]
            if np.all(np.abs(window) >= thr*0.8) and np.all(np.sign(window) == sign_mean):
                i0 = k; break
        if i0 is None:
            cand = np.where(sel)[0]
            if cand.size == 0: return
            i0 = int(cand[0])

        # 2) Reta tangente local em P1
        n_total = tx.size
        n_win = max(5, min(50, int(0.03 * n_total)))
        j1 = i0; j2 = min(n_total, i0 + n_win)
        if j2 - j1 < 3: j2 = min(n_total, i0 + 3)
        try:
            coeff = np.polyfit(tx[j1:j2], yy[j1:j2], 1)  # y ≈ s*x + b
            s = float(coeff[0]); x0 = float(tx[i0]); y0 = float(yy[i0])
            b = y0 - s * x0
        except Exception:
            x0 = float(tx[i0]); y0 = float(yy[i0]); s = float(dydt[i0]); b = y0 - s * x0

        # 3) P2: onde reta tangente cruza u(t) mapeado → resolver erro(x) = y_line - y_u = 0
        #    y_u é u(t) mapeado ao eixo esquerdo.
        def _err_at(ix):
            x = float(tx[ix])
            y_line = s * x + b
            y_u    = self._u_to_ydata(x, float(uu_r[ix]))
            return y_line - y_u

        # procure mudança de sinal do erro após i0
        root_x = None
        last_e = _err_at(i0)
        for j in range(i0+1, tx.size):
            e = _err_at(j)
            if np.isfinite(last_e) and np.isfinite(e) and (last_e == 0 or e == 0 or (last_e * e) < 0):
                # interpolação linear para raiz
                xA, xB = float(tx[j-1]), float(tx[j])
                if (e - last_e) != 0:
                    root_x = xA - last_e * (xB - xA) / (e - last_e)
                else:
                    root_x = xA
                break
            last_e = e

        if root_x is None:
            # fallback: ponto de menor distância em pixels (como estava)
            best_j = None; best_px = None
            for j in range(i0, tx.size):
                xj = float(tx[j]); y_line = s * xj + b
                y_u = self._u_to_ydata(xj, float(uu_r[j]))
                py_line = self.ax_y.transData.transform((xj, y_line))[1]
                py_u    = self.ax_y.transData.transform((xj, y_u))[1]
                dist_px = abs(py_line - py_u)
                if (best_px is None) or (dist_px < best_px):
                    best_px = dist_px; best_j = j
            if best_j is None: return
            x2 = float(tx[best_j]); y2 = float(s * x2 + b)
        else:
            x2 = float(root_x); y2 = float(s * x2 + b)

        self.kp_points = [(x0, y0), (x2, y2)]
        if self.kp_line is None:
            (self.kp_line,) = self.ax_y.plot([x0, x2], [y0, y2], linestyle='-', color='k', lw=1.5, label='Kp')
        else:
            self.kp_line.set_data([x0, x2], [y0, y2]); self.kp_line.set_linestyle('-')
            self.kp_line.set_color('k'); self.kp_line.set_linewidth(1.5)
        self._kp_update_text()
        self.draw_idle()
