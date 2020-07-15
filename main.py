from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from ulauncher.api.shared.action.OpenUrlAction import OpenUrlAction                   #delete this line
from ulauncher.api.shared.action.CopyToClipboardAction import CopyToClipboardAction   # test
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction   # test

import os
import sqlite3


class Extension(Extension):

    def __init__(self):
        super(Extension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())

##############################
# events
##############################

class KeywordQueryEventListener(EventListener):

    def on_event(self, event, extension): 
        query = event.get_argument() or str()
        if len(query.strip()) == 0: #<--------- in case the extension is called but there is nothing in input
            
            global string_list
            
            string_list.clear() #clear the list so it won't repeat the items in case of retyping
            read_database()
            print (string_list)
            
            #=============================
			# Copy
			#=============================
            if len(string_list) == 0:
            	return RenderResultListAction([ # this is from Ulauncher
                ExtensionResultItem(icon='images/icon.png', #image
                                    name='Your list is empty. Type "add" to add a new item', # text that appears when you type "delete"
                                    description="Or click here to access our GitHub page for help",
                                    on_enter=OpenUrlAction("http://www.google.com"))
            	])
            	#return RenderResultListAction(items)
            
            else:
            	items = [] #list thst goes to render
            	
            	for string_list_item in string_list:
            		if len(string_list_item[1]) < 40:
            			items.append(ExtensionResultItem(icon='images/icon.png', name=string_list_item[1], description='Copy this to your clipboard', on_enter=CopyToClipboardAction(string_list_item[1])))
            		else:
            			items.append(ExtensionResultItem(icon='images/icon.png', name=string_list_item[1][0:40] + "...", description=f'Copy this to your clipboard. ({len(string_list_item[1])} characters)', on_enter=CopyToClipboardAction(string_list_item[1])))
            	return RenderResultListAction(items)
            
        
        #=============================
		# input
		#=============================    
        elif query.strip()[0:3] == "add": #
            
            items = [] #this list goes to render
            
            data = {"action": "add", "id": query[4:]}
            items.append(ExtensionResultItem(icon='images/icon.png', name="I'm done!", description="New item: " + query[4:], on_enter=ExtensionCustomAction(data)))
            	
            return RenderResultListAction(items)

        
        #=============================
		# Delete 
		#=============================
        elif query.strip()[0:6] == "delete": 
			
            string_list.clear() #clear the list so it won't repeat the items in case of retyping
            read_database()
            print (string_list)
            
            items = [] #this list goes to render
            
            for string_list_item in string_list:
            	data = {"action": "delete", "id": string_list_item[0]}
            	items.append(ExtensionResultItem(icon='images/icon.png', name=string_list_item[1], description='Delete this item from your list', on_enter=ExtensionCustomAction(data, keep_app_open=True)))
            	
            return RenderResultListAction(items)

        #=============================
		# anything else 
		#=============================
        else:
            return RenderResultListAction([ # this is from Ulauncher
                ExtensionResultItem(icon='images/icon.png', #image
                                    name='Are you lost?', # text that appears when you type "delete"
                                    description="Open our help section on GitHub",
                                    on_enter=OpenUrlAction("http://www.google.com"))
            ])


##############################
# function caller
##############################
class ItemEnterEventListener(EventListener):
	
	def on_event(self, event, extension):
		#print("I WAS CALLED!!!")
		data = event.get_data()
		#print(data)
		
		if data["action"] == "add":
			#print("input called")
			#print(data["id"])
			add_item(data["id"])
		
		elif data["action"] == "delete":
			#print("delete called")
			#print(data["id"])
			delete_item(data["id"])
		



string_list = []

##############################
# database functions
##############################
# Read/create database
#=============================
def read_database():
	global string_list
	
	#pre_path = os.getcwd()
	path = os.getcwd()
	if "ulauncher" not in path:
		path = path + "/.local/share/ulauncher/extensions/get-it-fast"
	#path = pre_path + "/.local/share/ulauncher/extensions/get-it-fast/"
	print(path)
	
	try: #read the database
		print("reading the database")
		conn = sqlite3.connect(path + '/' + 'text_database.db')
		cursor = conn.cursor()

		# lendo os dados
		cursor.execute("""
		SELECT * FROM texts;
		""")

		for line in cursor.fetchall():
			#print(line)
			if line[0] not in string_list: #it doesn't seems to work as I expected.
				string_list.append(line)

		conn.close()
		
		print(f"string_list após read_database:")
		print(string_list)
		
	
	except: #create a database if it does not exists
		print("creating a database")
		conn = sqlite3.connect(path + '/' + 'text_database.db')

		# definindo um cursor
		cursor = conn.cursor()

		# criando a tabela (schema)
		cursor.execute("""CREATE TABLE texts (
					id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
					text TEXT NOT NULL
			)
			""")


		conn.commit()

		print('Tabela criada com sucesso.')
		# desconectando...
		conn.close()
		
		read_database()

#=============================
# insert item to database
#=============================
def add_item(text):
	print(f"insert item called to insert: {text}")
	global string_list
	
	insert_text = str(text)
	
	#string_list.append(text)
	
	conn = sqlite3.connect('text_database.db')
	cursor = conn.cursor()

	# inserindo dados na tabela
	cursor.execute("""
	INSERT INTO texts (text)
	VALUES (?)
	""", (insert_text,) )


	# gravando no bd
	conn.commit()

	print('Dados inseridos com sucesso.')

	conn.close()

#=============================
# delete item from database
#=============================
def delete_item(num):
	global string_list
	
	conn = sqlite3.connect('text_database.db')
	
	cursor = conn.cursor()
	cursor.execute("""
	DELETE FROM texts
	WHERE id = ?
	""", (num,))
	
	conn.commit()
	
	print('Registro excluido com sucesso.')
	
	conn.close()
	


if __name__ == '__main__':
    Extension().run()
