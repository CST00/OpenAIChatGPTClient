import openai
import PySimpleGUI as sg
import json

####
openai.api_key = '~Your API Key~'
####


#           Variable Storage

theme_list = sg.theme_list()
default_theme = 'GrayGrayGray'
memlimit = 5
totaltokens = 0
config_file = "config.json"
messagestorage = [{"role":"system","content":"You are a helpful assistant."}]

#this function will be used to call the api and return the response
def helper_api_call(messagestorage) :
    try:
        query = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messagestorage)
    except Exception as e:
        print('Error: ' + str(e))
        query = None  
    return query

# Load the configuration file or create an empty dictionary if it does not exist
try:
    with open(config_file, "r") as f:
        config = json.load(f)
except FileNotFoundError:
    config = {}

# Get the stored PySimpleGUI theme or use the default theme
selected_theme = config.get("theme", default_theme)
sg.theme(selected_theme)


# GUI for the Top Left column - Currrently has the token counter and the memory limit
tokens_column = [
    [sg.Text(text='Message Memory',pad=((10,50),(5,5)))],[sg.DropDown(values=[i for i in range(1,11)], readonly=True,enable_events=True ,size=(10, 1), key='memlim',default_value=memlimit,pad=((0,63),(20,20)))],
    [sg.Text(text="Tokens:", key="Tokens", auto_size_text=True, tooltip='This is the total number of tokens the last query cost', justification='left',pad=((0,100),(10,5)))],
    [sg.Text(text="Total Tokens:", auto_size_text=True, key="Total", tooltip='This is the total number of tokens for the session, 1000 tokens = .0006¢', justification='left',pad=((0,65),(10,5)))]
]
# GUI for the Top Right column - Currently has the model selector and the theme selector and the append to output box
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
# GUI for the bottom column - Currently has the output box and the input box
input_output_column = [
    [sg.Multiline( font=('Sans Serif', 12), justification='right', key="output", expand_x=True, expand_y=True)],
    [sg.Text(text="Enter a message:"), sg.Input(font="italics", do_not_clear=False, key="Input1", expand_x=True),
     sg.Button(button_text="Send", bind_return_key=True)]
]

layout = [
    [sg.Column(tokens_column,justification="left", element_justification="center",expand_x=True),
    sg.Column(boxes_column, justification="right",element_justification='center',expand_x=True)],
    [sg.Column(input_output_column,justification="c", element_justification="right",expand_x=True,expand_y=True)]
]

window = sg.Window('Chatbot', layout,finalize=True,resizable=True,)

# set the minumum window size - things get weird if you make it too small
width,height = window.get_screen_dimensions()
window.set_min_size((int(width/3),int(height/2)))

while True:
    event, values = window.read()

    #if the message storage is greater than the memory limit remove the oldest message
    if len(messagestorage) > memlimit:
        messagestorage.pop(0)
    
    #when the window is closed or the exit button is pressed
    if event == sg.WIN_CLOSED or event == 'Exit':
        sg.WINDOW_CLOSED
        break
    #when the theme preview button is pressed call the built in theme previewer
    if event == 'Theme Preview':
        sg.theme_previewer()

    #when the theme is changed in the drop down menu
    if event == 'Theme2':
        config['theme'] = values['Theme2']
        with open(config_file, "w") as f:
            json.dump(config, f)

    #when the memory limit is changed
    if event == 'memlim':
        memlimit = values['memlim']
        if len(messagestorage) > memlimit:
            messagestorage = messagestorage[-memlimit:]

    #When you select a Instructor setting
    if event == 'Drop':
        messagestorage.clear
        if values['Drop']=='Teacher':
           messagestorage.append({"role": "system", "content": "You are a teacher, explain things thoroughly and in depth"})
        elif values['Drop']=='Business':
          messagestorage.append({"role": "system", "content": "You are a business man, be professional and concise"})
        elif values['Drop']=='Normal':
            messagestorage.append({"role": "system", "content": "You are a helpful assistant."})


    ### Where the actual chatbot stuff happens ###

    #when the send button is pressed or enter is pressed
    if (event == 'Send' or event == '_Enter') and values['Input1'] != '':
        #take the value of the input box and print it to the output box
        window['output'].update('User: '+values['Input1']+'\n\n',append=True,text_color_for_value='#555555')  
        messagestorage.append({"role": "user", "content": values["Input1"]})

        #pass the message to the helper function using the long operation function so the window doesnt freeze
        window.perform_long_operation(lambda :helper_api_call(messagestorage),'-END KEY-')
        

    #when the helper function is done running
    if (event == '-END KEY-'):
        query = values['-END KEY-']
        if query is not None:
            messagestorage.append(query['choices'][0]['message'])
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
