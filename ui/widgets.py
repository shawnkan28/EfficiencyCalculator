from PyQt5 import QtWidgets as qtw, QtGui as qtg


def img_widget(path):
    img = qtg.QPixmap(path)
    img_lbl = qtw.QLabel()
    img_lbl.setPixmap(img)
    img_lbl.resize(img.width(), img.height())
    return img_lbl


def cb_widget(_list, searchable=False, index_change_event=None):
    cb = qtw.QComboBox()
    cb.addItems(_list)

    # make searchable
    if searchable:
        cb.setEditable(True)
        cb.setInsertPolicy(qtw.QComboBox.NoInsert)
        cb.completer().setCompletionMode(qtw.QCompleter.PopupCompletion)

    # add index change event
    if index_change_event:
        cb.currentIndexChanged.connect(index_change_event)

    return cb
