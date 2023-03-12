import openai
import tkinter as tk
import PySimpleGUI as sg
import json
openai.api_key = '~API KEY HERE~'

theme_list = sg.theme_list()
#get the theme in storage]
memlimit = 5
config_file = "config.json"
messagestorage = [{"role":"system","content":"You are a helpful assistant."}]
# Load the configuration file or create an empty dictionary if it does not exist
try:
    with open(config_file, "r") as f:
        config = json.load(f)
except FileNotFoundError:
    config = {}

# Get the stored PySimpleGUI theme or use the default theme
default_theme = 'GrayGrayGray'
selected_theme = config.get("theme", default_theme)
sg.theme(selected_theme)

def helper_api_call(messagestorage) :
    #this function will be used to call the api and return the response
    try:
        query = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messagestorage)
    except Exception as e:
        print('Error: ' + str(e))
        query = None  
    return query
   # messages=[{"role":"user","content":values['Input1']}]

tokens_column = [
    [sg.Text(text='Message Memory',pad=((10,50),(5,5)))],[sg.DropDown(values=[i for i in range(1,11)], readonly=True,enable_events=True ,size=(10, 1), key='memlim',default_value=memlimit,pad=((0,63),(20,20)))],
    [sg.Text(text="Tokens:", key="Tokens", auto_size_text=True, tooltip='This is the total number of tokens the last query cost', justification='left',pad=((0,100),(10,5)))],
    [sg.Text(text="Total Tokens:", auto_size_text=True, key="Total", tooltip='This is the total number of tokens for the session, 1000 tokens = .0006¢', justification='left',pad=((0,65),(10,5)))]
    
]

boxes_column = [
    [sg.Text(text="Select a model", key="Model", auto_size_text=True, tooltip='Set the mode of the GPT instructor, normal is chat bot mode and the other are self explanatory',
     justification='left',pad=((0,100),(5,5))),
     sg.Text(text="Select a theme", key="Theme", auto_size_text=True, tooltip='Set the theme of the window-this wont take affect till the next restart', justification='right')],
    [sg.Combo(['Normal','Business','Teacher'],default_value='Normal',key='Drop',readonly=True,size=20,pad=((10,10),(20,20)),enable_events=True),
     sg.DropDown(theme_list,pad=((10,10),(20,20)),default_value=sg.theme(),key ='Theme2',readonly=True,size=20,enable_events=True),
     sg.Button(button_text='Theme Preview',auto_size_button=True)],
    [sg.Text(text="Append to output", key="append", auto_size_text=True, tooltip='Whatever is typed in this box will be added to the end of your request',
     justification='center')],
    [sg.Multiline( font=('Helvetica', 10),justification='r', key="append",auto_size_text=True,pad=5)]

]

input_output_column = [
    [sg.Multiline( font=('Sans Serif', 12), justification='right', key="output", expand_x=True, expand_y=True)],
    [sg.Text(text="Enter a message:"), sg.Input(font="italics", do_not_clear=False, key="Input1", expand_x=True),
     sg.Button(button_text="Send", bind_return_key=True)]
]
#fill a list with every pysimplegui theme
theme_list = sg.theme_list()

layout = [
    [sg.Column(tokens_column,justification="left", element_justification="center",expand_x=True),
    sg.Column(boxes_column, justification="right",element_justification='center',expand_x=True)],
    [sg.Column(input_output_column,justification="c", element_justification="right",expand_x=True,expand_y=True)]
    

]

window = sg.Window('Chatbot', layout,finalize=True,resizable=True,)


width,height = window.get_screen_dimensions()
width = int(width)
height = int(height)
width  = round(width)
height = round(height)


window.set_min_size((int(width/3),int(height/2)))

totaltokens = 0
while True:
    event, values = window.read()
    output = ''

    if len(messagestorage) > memlimit:
        messagestorage.pop(0)
        #remove the first element of the message list
    if event == sg.WIN_CLOSED or event == 'Exit':
        sg.WINDOW_CLOSED
        break
    if event == 'Theme Preview':
        sg.theme_previewer()
    if event == 'Theme2':
        config['theme'] = values['Theme2']
        with open(config_file, "w") as f:
            json.dump(config, f)
    if event == 'memlim':
        memlimit = values['memlim']
        if len(messagestorage) > memlimit:
            messagestorage = messagestorage[-memlimit:]
        
    if event == 'Drop':
        messagestorage.clear
        if values['Drop']=='Teacher':
           messagestorage.append({"role": "system", "content": "You are a teacher, explain things thoroughly and in depth"})
        elif values['Drop']=='Business':
          messagestorage.append({"role": "system", "content": "You are a business man, be professional and concise"})
        elif values['Drop']=='Normal':
            messagestorage.append({"role": "system", "content": "You are a helpful assistant."})


    


    if (event == 'Send' or event == '_Enter') and values['Input1'] != '':
        #take the value of the input box and print it to the output box
        window['output'].update('User: '+values['Input1']+'\n\n',append=True,text_color_for_value='#555555')  
        messagestorage.append({"role": "user", "content": values["Input1"]})

        window.perform_long_operation(lambda :
                              helper_api_call(messagestorage),
                              '-END KEY-')
        


    if (event == '-END KEY-'):
        query = values['-END KEY-']
        if query is not None:
            output = str(query['choices'][0]['message']['content'])

            #replace the newlines
            output = output.replace('\n',' ')
             #write to the multiline box
            window['output'].update('Bot:'+str(output)+'\n\n',append=True)
            #set thet okens for last query and total query

            window['Tokens'].update('Tokens: '+ str(query['usage']['total_tokens']))
            totaltokens += query['usage']['total_tokens']
            window['Total'].update('Total Tokens: '+ str(totaltokens))
            #clear the input box