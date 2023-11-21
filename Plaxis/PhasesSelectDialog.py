from PySide6 import QtWidgets
from PySide6.QtCore import (QRect, Qt, QTimer, Slot)
from PySide6.QtWidgets import (QAbstractItemView, QDialog, QDialogButtonBox, QListWidget, QMessageBox)
from typing import List

app = None

if not QtWidgets.QApplication.instance():
    app = QtWidgets.QApplication([])
else:
    app = QtWidgets.QApplication.instance()

class PhasesSelectDialog(QDialog):
    PhasesList:QListWidget = None
    OKCancelBtn:QDialogButtonBox = None
    SelectedItems:List[int] = None
    RequiredSelectedItemNos:int = 0
    Title:str = ""
    
    timer:QTimer = None
    Timeout:int = 0

    def __init__(self, phasesList:List[str], selectedItemIndices:List[int], title:str = "Please Select {} Phases",
                 timeout:int = 5, unlimited_items = False) -> None:
        super().__init__()

        if not self.objectName():
            self.setObjectName(u"PhasesSelectDialog")
        self.setWindowModality(Qt.WindowModal)
        self.setFixedSize(400, 647)
        self.setModal(True)
        self.PhasesList = QListWidget(self)
        self.PhasesList.setObjectName(u"PhasesList")
        self.PhasesList.setGeometry(QRect(20, 20, 361, 581))
        self.PhasesList.setSelectionMode(QAbstractItemView.MultiSelection)
        self.OKCancelBtn = QDialogButtonBox(self)
        self.OKCancelBtn.setObjectName(u"OKCancelBtn")
        self.OKCancelBtn.setGeometry(QRect(110, 610, 156, 24))
        self.OKCancelBtn.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        self.OKCancelBtn.setCenterButtons(False)

        #Process PhasesList
        self.PhasesList.addItems(phasesList)
        self.SelectedItems = selectedItemIndices
        self.Unlimited_items = unlimited_items
        if self.Unlimited_items:
            self.RequiredSelectedItemNos = 9999
        else:
            self.RequiredSelectedItemNos = len(selectedItemIndices)
        for itemIndex in selectedItemIndices:
            self.PhasesList.item(itemIndex).setSelected(True)
        self.PhasesList.itemSelectionChanged.connect(self.PhasesList_Change)

        self.Timeout = timeout
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.Timer_OnTime)
        self.Timer_OnTime()
        self.timer.start()

        self.Title = title.format(self.RequiredSelectedItemNos)
        self.setWindowTitle(self.Title)

        self.OKCancelBtn.accepted.connect(self.OK)
        self.OKCancelBtn.rejected.connect(self.Cancel)

        self.finished.connect(self.Dialog_Close)
        self.activateWindow()

    @Slot()
    def PhasesList_Change(self):
        if (not self.timer is None) and self.timer.isActive():
            self.timer.stop()
        selectedItems = self.PhasesList.selectedItems()
        if not self.Unlimited_items:
            if len(selectedItems) > self.RequiredSelectedItemNos:
                selectedItems[0].setSelected(False)

    @Slot()
    def Timer_OnTime(self):
        self.setWindowTitle(self.Title + " : Timeout in {:d} second...".format(self.Timeout))
        if self.Timeout < 0:
            self.accept()
        self.Timeout -= 1

    @Slot(int)
    def Dialog_Close(self, result):
        self.SelectedItems.clear()
        for index in self.PhasesList.selectedIndexes():
            self.SelectedItems.append(index.row())

    @Slot()
    def OK(self):
        if self.Unlimited_items:
            self.accept()
        else:
            if len(self.PhasesList.selectedItems()) == self.RequiredSelectedItemNos:
                self.accept()
            else:
                msgBox = QMessageBox()
                msgBox.setWindowTitle("Warning!")
                msgBox.setText("Please select {} phases!".format(self.RequiredSelectedItemNos))
                msgBox.exec()

    @Slot()
    def Cancel(self):
        self.reject()