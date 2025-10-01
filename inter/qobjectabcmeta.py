from react.qt_compat import QObject
from abc import ABCMeta

class QObjectABCMeta(ABCMeta, type(QObject)):
    """Metaclasse que combina ABCMeta e QMetaObject para evitar conflitos."""
    pass