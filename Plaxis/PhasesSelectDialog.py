from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QRect, Qt, QTimer, Slot)
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QDialog,
    QDialogButtonBox, QListWidget, QMessageBox)
from typing import List

app = None

def InitQt():
    global app
    if app is None:
        try:
            app = QApplication([])
        except:
            pass

class Ui_PhasesSelectDialog(object):
    def setupUi(self, PhasesSelectDialog):
        if not PhasesSelectDialog.objectName():
            PhasesSelectDialog.setObjectName(u"PhasesSelectDialog")
        PhasesSelectDialog.setWindowModality(Qt.WindowModal)
        PhasesSelectDialog.setFixedSize(400, 647)
        PhasesSelectDialog.setModal(True)
        self.PhasesList = QListWidget(PhasesSelectDialog)
        self.PhasesList.setObjectName(u"PhasesList")
        self.PhasesList.setGeometry(QRect(20, 20, 361, 581))
        self.PhasesList.setSelectionMode(QAbstractItemView.MultiSelection)
        PhasesSelectDialog.PhasesList = self.PhasesList
        self.OKCancelbtn = QDialogButtonBox(PhasesSelectDialog)
        self.OKCancelbtn.setObjectName(u"OKCancelbtn")
        self.OKCancelbtn.setGeometry(QRect(110, 610, 156, 24))
        self.OKCancelbtn.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        self.OKCancelbtn.setCenterButtons(False)
        PhasesSelectDialog.OKCancelBtn = self.OKCancelbtn

        self.retranslateUi(PhasesSelectDialog)

        QMetaObject.connectSlotsByName(PhasesSelectDialog)
    # setupUi

    def retranslateUi(self, PhasesSelectDialog):
        PhasesSelectDialog.setWindowTitle(QCoreApplication.translate("PhasesSelectDialog", u"Dialog", None))
    # retranslateUi

class PhasesSelectDialog(QDialog):
    PhasesList:QListWidget = None
    OKCancelBtn:QDialogButtonBox = None
    SelectedItems:List[int] = None
    RequiredSelectedItemNos:int = 0
    Title:str = ""
    
    timer:QTimer = None
    Timeout:int = 0

    def __init__(self, phasesList:List[str], selectedItemIndices:List[int], title:str = "Please Select {} Phases", timeout:int = 5) -> None:
        super().__init__()
        self.ui = Ui_PhasesSelectDialog()
        self.ui.setupUi(self)

        #Process PhasesList
        self.PhasesList.addItems(phasesList)
        self.SelectedItems = selectedItemIndices
        self.RequiredSelectedItemNos = len(selectedItemIndices)
        for itemIndex in selectedItemIndices:
            self.PhasesList.item(itemIndex).setSelected(True)
        self.PhasesList.itemSelectionChanged.connect(self.PhasesList_Change)

        self.Timeout = timeout * 1000
        self.timer = QTimer(self)
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.Timer_OnTime)
        self.timer.start()

        self.Title = title.format(self.RequiredSelectedItemNos)
        self.setWindowTitle(self.Title)

        self.OKCancelBtn.accepted.connect(self.OK)
        self.OKCancelBtn.rejected.connect(self.Cancel)

        self.finished.connect(self.Dialog_Close)

    @Slot()
    def PhasesList_Change(self):
        if (not self.timer is None) and self.timer.isActive():
            self.timer.stop()
        selectedItems = self.PhasesList.selectedItems()
        if len(selectedItems) > self.RequiredSelectedItemNos:
            selectedItems[0].setSelected(False)

    @Slot()
    def Timer_OnTime(self):
        self.setWindowTitle(self.Title + " : Timeout in {:d} second...".format(int(self.Timeout/1000)))
        if self.Timeout < 0:
            self.accept()
        self.Timeout -= 100

    @Slot(int)
    def Dialog_Close(self, result):
        self.SelectedItems.clear()
        for index in self.PhasesList.selectedIndexes():
            self.SelectedItems.append(index.row())

    @Slot()
    def OK(self):
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
