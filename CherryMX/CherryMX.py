import adsk.core, traceback
import re
import json
import codecs

width = 1.905

def parseLayout(layout):
	positions = []

	x = 0
	y = 0

	for row in layout:
		if type(row) is not list:
			continue

		elementWidth = 1
		for element in row:
			if type(element) is dict:
				x += element.get("x", 0)
				y += element.get("y", 0)
				elementWidth = element.get("w", 1)

			elif type(element) is str:
				positions.append((x + (elementWidth - 1) / 2, y, element))
				x += elementWidth
				elementWidth = 1

		x = 0
		y += 1

	return positions

def addSwitch(occurence, x, y):
	destTransform = occurence.transform
	destTransform.translation = adsk.core.Vector3D.create(destTransform.translation.x + x, destTransform.translation.y + y, destTransform.translation.z)

	newComponent = occurence.assemblyContext.component.occurrences.addExistingComponent(occurence.component, destTransform)

def run(context):
	ui = None

	try:
		app = adsk.core.Application.get()
		ui = app.userInterface

		occurence = ui.selectEntity("Select Cherry MX component", "Occurrences").entity

		file = ui.createFileDialog()
		file.title = "Select layout JSON file"
		file.filter = "*.json"

		if(file.showOpen() != adsk.core.DialogResults.DialogOK):
			return None

		with codecs.open(file.filenames[0], encoding="utf-8") as jsonFile:
			layout = json.load(jsonFile)
			positions = parseLayout(layout)

			progressDialog = ui.createProgressDialog()
			progressDialog.show("Copying switches...", "Copying switch %v of %m...", 1, len(positions))

			for i in range(1, len(positions)):
				progressDialog.progressValue = i + 1
				(x, y, name) = positions[i]

				x = x * width
				y = y * width

				addSwitch(occurence, x, -y)

				if progressDialog.wasCancelled:
					return None

			progressDialog.hide()

	except:
		if ui:
			ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))