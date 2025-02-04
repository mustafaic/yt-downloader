self.list_film_title = QtWidgets.QLabel(self.list_media_frame)
self.list_film_title.setMinimumSize(QtCore.QSize(0, 30))
self.list_film_title.setMaximumSize(QtCore.QSize(16777215, 30))
font = QtGui.QFont()
font.setPointSize(9)
self.list_film_title.setFont(font)
self.list_film_title.setStyleSheet("color: white;")
self.list_film_title.setObjectName("list_film_title")
self.verticalLayout_8.addWidget(self.list_film_title)
self.progressBar = QtWidgets.QProgressBar(self.list_media_frame)
self.progressBar.setMaximumSize(QtCore.QSize(16777215, 30))
self.progressBar.setStyleSheet("color: white;")
self.progressBar.setProperty("value", 0)
self.progressBar.setObjectName("progressBar")
self.verticalLayout_8.addWidget(self.progressBar)
self.verticalLayout_7.addWidget(self.list_media_frame, 0, QtCore.Qt.AlignmentFlag.AlignTop)



self.list_film_title.setText(_translate("MainWindow", "Title"))
