import openai
import PySimpleGUI as sg
import json
import time
import keyboard

####
openai.api_key = ''
####


#           Open Config File - Has API key and Theme
config_file = "config.json"

try:
    with open(config_file, "r") as f:
        config = json.load(f)
except FileNotFoundError:
    config = {}



#           Variable Storage
theme_list = sg.theme_list()
default_theme = 'GrayGrayGray'
memlimit = 5
totaltokens = 0
messagestorage = [{"role":"system","content":"You are a helpful assistant."}]
selected_theme = config.get("theme", default_theme)
openai.api_key = config.get("api",'')

#this function will be used to call the api and return the response
def helper_api_call(messagestorage) :
    try:
        query = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messagestorage)
       
    except Exception as e:
        window['output'].update('Error: ' + str(e) + 'Press F12 + Send if you need to reinsert api key',append=True,justification='l',text_color='red')
        query = None  
    return query

#Run a timer while the api is being called updating the timer textbox
def display_timer():
    timer = 0
    window['timer'].update(visible=True)


    while window['timer'].visible==True:
        window['timer'].update(str(timer))
        timer += 1
        time.sleep(1)
        window.refresh()

       

#this function will be used to convert the hex color code to rgb
def hex_to_rgb(hex):
    """Return (red, green, blue) for the color given as #rrggbb."""
    if(hex[0] == '#'):
        hex = hex[1:]
    else:
        #black
        return (255,255,255)
    result = []
    hlen = len(hex)
    #return a list
    #use regex to extract the hex values
    for i in range(0, hlen, 2):
        result.append(int(hex[i:i+2],16))

        
    return result
def rgb_to_hex(rgb):
    """Return color as #rrggbb for the given color values."""
    return '#%02x%02x%02x' % rgb

    

# Load the configuration file or create an empty dictionary if it does not exist

# Get the stored PySimpleGUI theme or use the default theme
selected_theme = config.get("theme", default_theme)
openai.api_key = config.get("api",'')
sg.theme(selected_theme)
bgcolorstart = sg.theme_button_color_background()
bgcolor = hex_to_rgb(bgcolorstart)
if bgcolorstart == '1234567890':
    bgcolorstart = 'black'

#if bgcolor is dark set the text color to white and if it is light set the text color to black
if bgcolor[0] < 128 and bgcolor[1] < 128 and bgcolor[2] < 128:
    textcolor = '#FF4500'
else:
    textcolor = '#f35390'
    

# GUI for the Top Left column - Currrently has the token counter and the memory limit
tokens_column = [
    [sg.Text(text='Message Memory',pad=((10,50),(5,5)))],[sg.DropDown(values=[i for i in range(1,11)], readonly=True,enable_events=True ,size=(10, 1),tooltip='This is how many previous messages will be sent with the current one so the bot can better understand the topic - more messages = better performance but cost more tokens.', key='memlim',default_value=memlimit,pad=((0,63),(20,20)))],
    [sg.Text(text="Tokens:", key="Tokens", auto_size_text=True, tooltip='This is the total number of tokens the last query cost', justification='left',pad=((0,100),(10,5)))],
    [sg.Text(text="Total Tokens:", auto_size_text=True, key="Total", tooltip='This is the total number of tokens for the session, 1000 tokens = .0006¢', justification='left',pad=((0,65),(10,5)))]
]
# GUI for the Top Right column - Currently has the model selector and the theme selector and the append to output box
boxes_column = [
    [sg.Text(text="Select an Instructor", key="Model", auto_size_text=True, tooltip='Set the mode of the GPT instructor, normal is chat bot mode, Teacher will explain things in depth and business should be more concise',
     justification='left',pad=((0,100),(5,5))),
     sg.Text(text="Select a theme", key="Theme", auto_size_text=True, tooltip='Set the theme of the window-this wont take affect till the next restart', justification='right')],
    [sg.Combo(['Normal','Business','Teacher'],default_value='Normal',key='Instructor',readonly=True,size=20,pad=((10,10),(20,20)),enable_events=True,tooltip='Set the mode of the GPT instructor, normal is chat bot mode, Teacher will explain things in depth and business should be more concise'),
     sg.DropDown(theme_list,pad=((10,10),(20,20)),default_value=sg.theme(),key ='Theme2',readonly=True,size=20,enable_events=True),
     sg.Button(button_text='Theme Preview',auto_size_button=True)],
    [sg.Text(text="Append to output", key="appendt", auto_size_text=True, tooltip='Whatever is typed in this box will be added to the end of your request',
     justification='center')],
    [sg.Input( font=('Helvetica', 10),justification='l', key="append",pad=5,)]
]
# GUI for the bottom column - Currently has the output box and the input box
input_output_column = [
    [sg.Multiline( font=('Sans Serif', 12), justification='right', key="output", expand_x=True, expand_y=True)],
    [sg.Text(text="Enter a message:"), sg.Multiline(font="italics", do_not_clear=False, key="Input1", expand_x=True,auto_size_text=True,no_scrollbar=True,enter_submits=True),
     sg.Button(button_text="Send", bind_return_key=True),sg.Text(text='',key='timer',visible=False)]
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
    elif event == sg.WIN_CLOSED or event == 'Exit':
        sg.WINDOW_CLOSED
        break
    #when the theme preview button is pressed call the built in theme previewer
    elif event == 'Theme Preview':
        sg.theme_previewer()

    #when the theme is changed in the drop down menu
    elif event == 'Theme2':
        config['theme'] = values['Theme2']
        with open(config_file, "w") as f:
            json.dump(config, f)

    #when the memory limit is changed
    elif event == 'memlim':
        memlimit = values['memlim']
        if len(messagestorage) > memlimit:
            messagestorage = messagestorage[-memlimit:]

    #When you select a Instructor setting
    elif event == 'Instructor':
        messagestorage.clear
        if values['Instructor']=='Teacher':
           messagestorage.append({"role": "system", "content": "You are a teacher, explain things thoroughly and in depth"})
        elif values['Instructor']=='Business':
          messagestorage.append({"role": "system", "content": "You are a business man, professional and concise"})
        elif values['Instructor']=='Normal':
            messagestorage.append({"role": "system", "content": "You are a helpful assistant."})

    #When you press f12 and activate another event to toggle the debug window
    elif  keyboard.is_pressed('F12') or (openai.api_key == '') or openai.api_key == None:
        #pop up the debug window
        tempapi =sg.PopupGetText('Insert API key here')
        #store the api key in the config file
        config['api'] = tempapi
        with open(config_file, "w") as f:
            json.dump(config, f)
        openai.api_key = tempapi
       
    ### Where the actual chatbot stuff happens ###

    #when the send button is pressed or enter is pressed
    elif (event == 'Send' or event == '_Enter') and values['Input1'] != '':
        #take the value of the input box and print it to the output box
        window['output'].update('User: '+values['Input1']+' '+values['append']+'\n\n',append=True)  
        messagestorage.append({"role": "user", "content": values["Input1"]+' '+values['append']})

        #pass the message to the helper function using the long operation function so the window doesnt freeze
        window.perform_long_operation(lambda :helper_api_call(messagestorage),'-END KEY-')
        window.perform_long_operation(display_timer,'endtimer')
        

    #when the helper function is done running
    elif (event == '-END KEY-'):
        query = values['-END KEY-']
        window['timer'].update('',visible=False)
        
        if query is not None:
            messagestorage.append(query['choices'][0]['message'])
            output = str(query['choices'][0]['message']['content'])

            #replace the newlines
            
             #write to the multiline box
            window['output'].update('Bot: ',append=True,justification='l',text_color_for_value=textcolor,)
            window['output'].update(str(output)+'\n',append=True,justification='l')
            window['output'].update('_'*50+'\n\n',justification='c',append=True,text_color_for_value=bgcolorstart)
            #set thet okens for last query and total query
            
            #hex code for very light gray
            
            window['Tokens'].update('Tokens: '+ str(query['usage']['total_tokens']))
            totaltokens += query['usage']['total_tokens']
            window['Total'].update('Total Tokens: '+ str(totaltokens))
            #clear the input box
            
