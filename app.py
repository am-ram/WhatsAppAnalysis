import streamlit as st
import pandas as pd
import numpy as np
import re
import emoji
import plotly.express as px
from collections import Counter
import matplotlib.pyplot as plt
from os import path
from PIL import Image
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import regex
import time
import sys
import inspect
import datetime
plt.style.use('dark_background')
#st.title('Whatsapp Group Chat Analysis')
st.markdown('<h1 style="background-color: #4F8BF9;text-align:center; border-radius:10px;font-size:50px"> Whatsapp Group Chat Analysis</h1>',unsafe_allow_html=True)
st.markdown('<h2 style="background-color: black;text-align:center;color:#fff; border-radius:10px;" >Ever wondered the insights your group could provide you with ???',unsafe_allow_html=True)
st.set_option('deprecation.showfileUploaderEncoding', False)


st.sidebar.title("About : ")
st.sidebar.markdown("This is a WebApp built with the help of streamlit,re & regex and is a NLP project done by Sai Ram.K")
st.sidebar.markdown('[![Sai Ram]\
					( https://img.shields.io/github/followers/am-ram?color=cyan&label=am-ram&logo=github&logoColor=white&style=for-the-badge)]\
					(https://github.com/am-ram)')
                   
    

st.sidebar.markdown('**How to export chat text file? (P.S : Not Available on Whatsapp Web)**')
st.sidebar.text('Follow the steps 👇:')
st.sidebar.text('1) Open the individual or group chat.')
st.sidebar.text('2) Tap options > More > Export chat.')
st.sidebar.text('3) Choose export without media.')
st.sidebar.text('4) Upload the file here.')
st.sidebar.markdown('*You are all set to go 😃*.')
st.sidebar.subheader('**FAQs**')
st.sidebar.markdown('**What happens to my data?**')
st.sidebar.markdown('The data you upload is not saved anywhere on this site or any 3rd party site i.e, not in any storage like DB/FileSystem/Logs.')
st.sidebar.markdown("**I am not getting insights for my chat...?**")
st.sidebar.markdown("This is a beta app and  **Currenly works only for text files having date format as dd/mm/yyyy** other formats will be uploaded soon.")

def visualize_emoji(data):
	total_emojis_list = list([a for b in messages_df.emoji for a in b])
	emoji_dict = dict(Counter(total_emojis_list))
	emoji_dict = sorted(emoji_dict.items(), key=lambda x: x[1], reverse=True)
	emoji_df = pd.DataFrame(emoji_dict, columns=['emoji', 'count'])
	fig = px.pie(emoji_df, values='count', names='emoji')
	fig.update_traces(textposition='inside', textinfo='percent+label')
	fig.update_layout(
    	margin=dict(
        	l=5,
        	r=5,
    	)
    )
	fig.update(layout_showlegend=False)
	return fig

def messages_as_time_moves_on(messages_df):
	date_df = messages_df.groupby("Date").sum()
	date_df.reset_index(inplace=True)
	fig = px.line(date_df, x="Date", y="MessageCount")
	fig.update_layout(
    	margin=dict(
        	l=5,
        	r=5,
    	)
    )
	return fig

def chatteraward(messages_df):
	auth = messages_df.groupby("Author").sum()
	auth.reset_index(inplace=True)
	fig = px.bar(auth, x="Author", y="MessageCount", color='Author', orientation = "v",
             color_discrete_sequence=["red", "green", "blue", "goldenrod", "magenta"],
             title="Chatterbox Award (P.S : For chats with less than 10 participants only)"
            )
	fig.update(layout_showlegend=False)
	fig.update_layout(
    	margin=dict(
        	l=5,
        	r=5,
    	)
    )
	return fig

def time_active(messages_df):
	messages_df['Time'].value_counts().head(10).plot.barh('c') # Top 10 Times of the day at which the most number of messages were sent
	plt.xlabel('Number of messages',size=20)
	plt.ylabel('Time',size=20)
	plt.tight_layout()

def words(messages_df):
	text = " ".join(review for review in messages_df.Message)
	stopwords = set(STOPWORDS)
	stopwords.update(["ra", "ga", "na", "ani", "em", "ki", "ah","ha","la","eh","ne","le","ni","lo","Ma","Haa","ni","deleted","message"])
	wordcloud = WordCloud(stopwords=stopwords, background_color="white",height=640, width=800).generate(text)
	# Display the generated image the matplotlib way:
	plt.imshow(wordcloud, interpolation='bilinear')
	plt.xticks([])
	plt.yticks([])
	plt.tight_layout()

def day(messages_df):
	messages_df['Date'].value_counts().head(10).plot.barh('c')
	plt.xlabel('Number of Messages',size=20)
	plt.ylabel('Date',size=20)
	plt.tight_layout()


def split_count(text):

    emoji_list = []
    data = regex.findall(r'\X', text)
    for word in data:
        if any(char in emoji.UNICODE_EMOJI for char in word):
            emoji_list.append(word)

    return emoji_list

def stats(data):
    """
        This function takes input as data and return number of messages and total emojis used in chat.
    """
    total_messages = data.shape[0]
    media_messages = data[data['Message'] == '<Media omitted>'].shape[0]
    emojis = sum(data['emoji'].str.len())
    
    return "Total Messages 💬: {} \n Total Media 🎬: {} \n Total Emoji's 😂: {}".format(total_messages, media_messages, emojis)

def startsWithDateAndTimeAndroid(s):
    pattern = '^([0-9]+)(\/)([0-9]+)(\/)([0-9]+), ([0-9]+):([0-9]+)[ ]?(AM|PM|am|pm)? -' 
    result = re.match(pattern, s)
    if result:
        return True
    return False

def startsWithDateAndTimeios(s):
    pattern = '^\[([0-9]+)([\/-])([0-9]+)([\/-])([0-9]+)[,]? ([0-9]+):([0-9][0-9]):([0-9][0-9])?[ ]?(AM|PM|am|pm)?\]' 
    result = re.match(pattern, s)
    if result:
        return True
    return False

def FindAuthor(s):
  s=s.split(":")
  if len(s)==2:
    return True
  else:
    return False

def getDataPointAndroid(line):   
    splitLine = line.split(' - ') 
    dateTime = splitLine[0]
    date, time = dateTime.split(', ') 
    message = ' '.join(splitLine[1:])
    if FindAuthor(message): 
        splitMessage = message.split(':') 
        author = splitMessage[0] 
        message = ' '.join(splitMessage[1:])
    else:
        author = None
    return date, time, author, message

def getDataPointios(line):
	splitLine = line.split('] ')
	dateTime = splitLine[0]
	if ',' in dateTime:
		date, time = dateTime.split(',')
	else:
		date, time = dateTime.split(' ')
	message = ' '.join(splitLine[1:])
	if FindAuthor(message):
		splitMessage = message.split(':')
		author = splitMessage[0]
		message = ' '.join(splitMessage[1:])
	else:
		author = None
	if time[5]==":":
		print(time)
		time = time[:5]+time[-3:]
	else:
		if 'AM' in time or 'PM' in time:
			time = time[:6]+time[-3:]
		else:
			time = time[:6]
	return date, time, author, message

def dateconv(date):
  year=''
  if '-' in date:
    year = date.split('-')[2]
    if len(year) == 4:
      return datetime.datetime.strptime(date, "[%d-%m-%Y").strftime("%Y-%m-%d")
    elif len(year) ==2:
      return datetime.datetime.strptime(date, "[%d-%m-%y").strftime("%Y-%m-%d")
  elif '/' in date:
    year = date.split('/')[2]
    if len(year) == 4:
      return datetime.datetime.strptime(date, "[%d/%m/%Y").strftime("%Y-%m-%d")
    if len(year) ==2:
      return datetime.datetime.strptime(date, "[%d/%m/%y").strftime("%Y-%m-%d")

uploaded_file = st.file_uploader("Upload Your Whatsapp Chat.(.txt file only!)", type="txt")
#uploaded_file = r'D:\Deployed Projects\WhatsappAnalysis\UnofficialGroup.txt'
if uploaded_file is not None:
	@st.cache(allow_output_mutation=True)
	def load_data(uploaded_file):
		device=''
		if '[' in next(uploaded_file):
			device='ios'
		else:
			device="android"
		next(uploaded_file)
		parsedData = []
		messageBuffer = []
		date, time, author = None, None, None
		for i in uploaded_file:
			line = i
			if not line:
				 break
			if device=="ios":
				line = line.strip()
				if startsWithDateAndTimeios(line):
					if len(messageBuffer) > 0:
						parsedData.append([date, time, author, ' '.join(messageBuffer)])
					messageBuffer.clear()
					date, time, author, message = getDataPointios(line)
					messageBuffer.append(message)
				else:
					line= (line.encode('ascii', 'ignore')).decode("utf-8")
					if startsWithDateAndTimeios(line):
						if len(messageBuffer) > 0:
							parsedData.append([date, time, author, ' '.join(messageBuffer)])
						messageBuffer.clear()
						date, time, author, message = getDataPointios(line)
						messageBuffer.append(message)
					else:
						messageBuffer.append(line)

			else:
				line = line.strip()
				if startsWithDateAndTimeAndroid(line):
					if len(messageBuffer) > 0:
						parsedData.append([date, time, author, ' '.join(messageBuffer)])
					messageBuffer.clear()
					date, time, author, message = getDataPointAndroid(line)
					messageBuffer.append(message)
				else:
					messageBuffer.append(line)

		if device =='android':					
			df = pd.DataFrame(parsedData, columns=['Date', 'Time', 'Author', 'Message'])
			df["Date"] = pd.to_datetime(df["Date"])
			df = df.dropna()
			df["emoji"] = df["Message"].apply(split_count)
			URLPATTERN = r'(https?://\S+)'
			df['urlcount'] = df.Message.apply(lambda x: re.findall(URLPATTERN, x)).str.len()
			return df;
		else:
			df = pd.DataFrame(parsedData, columns=['Date', 'Time', 'Author', 'Message']) # Initialising a pandas Dataframe.
			df = df.dropna()
			df["Date"] = df["Date"].apply(dateconv)
			df["Date"] = pd.to_datetime(df["Date"],format='%Y-%m-%d')
			df["emoji"] = df["Message"].apply(split_count)
			URLPATTERN = r'(https?://\S+)'
			df['urlcount'] = df.Message.apply(lambda x: re.findall(URLPATTERN, x)).str.len()
			return df;

	data = load_data(uploaded_file)

	authorlist = list(data.Author.unique())
	authorlist.insert(0,'All')
	st.subheader("**Who's Stats do you want to see?**");st.write('Select the name of the pariticipant from the dropdown menu.')
    
	option = st.selectbox("", authorlist)
	if option == "All":
		name="Group"
		total_messages = data.shape[0]
		link_messages= data[data['urlcount']>0]
		deleted_messages=data[(data["Message"] == " You deleted this message")| (data["Message"] == " This message was deleted")| (data["Message"] == " This message was deleted.")|(data["Message"] == " You deleted this message.")]
		print(deleted_messages.shape[0])
		media_messages = data[(data['Message'] == ' <Media omitted>')|(data['Message'] == ' image omitted')|(data['Message'] == ' video omitted')|(data['Message'] == ' sticker omitted')].shape[0]
		emojis = sum(data['emoji'].str.len())
		links = np.sum(data.urlcount)
		st.subheader("**%s's total messages 💬**"% name)
		st.markdown(total_messages)
		st.subheader("**%s's total media 🎬**"% name)
		st.markdown(media_messages)
		st.subheader("**%s's total emojis 😂**"% name)
		st.markdown(emojis)
		st.subheader("**%s's total links**"% name)
		st.markdown(links)
		media_messages_df = data[(data['Message'] == ' <Media omitted>')|(data['Message'] == ' image omitted')|(data['Message'] == ' video omitted')|(data['Message'] == ' sticker omitted')]
		messages_df = data.drop(media_messages_df.index)
		messages_df = messages_df.drop(deleted_messages.index)
		messages_df = messages_df.drop(link_messages.index)
		messages_df['Letter_Count'] = messages_df['Message'].apply(lambda s : len(s))
		messages_df['Word_Count'] = messages_df['Message'].apply(lambda s : len(s.split(' ')))
		messages_df["MessageCount"]=1
		messages_df["emojicount"]= messages_df['emoji'].str.len()
		config={'responsive': True}
		st.header("**Some more Stats**")
		st.subheader("**%s's emoji distribution 😂**"% name)
		st.text("Hover on Chart to see details.")
		st.plotly_chart(visualize_emoji(data),use_container_width=True)
		st.subheader("**%s's messages as time moves on**"% name)
		st.text("Hover on Chart to see details.")
		st.plotly_chart(messages_as_time_moves_on(messages_df),use_container_width=True)
		st.subheader("**And the Chatterbox Award in the group goes to - **")
		st.text("Hover on Chart to see details.")
		st.plotly_chart(chatteraward(messages_df),use_container_width=True)
		st.subheader("**When is the %s most active?**"% name)
		time_active(messages_df)
		st.pyplot()
		time.sleep(0.2)
		st.subheader("**The most happening day for the %s was - **"% name)
		day(messages_df)
		st.pyplot()
		time.sleep(0.2)
		st.subheader("**%s's WordCloud **"% name)
		words(messages_df)
		st.pyplot()
	else:
		data = data[data.Author.eq(option)]
		total_messages = data.shape[0]
		link_messages= data[data['urlcount']>0]
		deleted_messages=data[(data["Message"] == " You deleted this message")| (data["Message"] == " This message was deleted.")|(data["Message"] == " You deleted this message.")]
		print(deleted_messages.shape[0])
		media_messages = data[(data['Message'] == ' <Media omitted>')|(data['Message'] == ' image omitted')|(data['Message'] == ' video omitted')|(data['Message'] == ' sticker omitted')].shape[0]
		emojis = sum(data['emoji'].str.len())
		links = np.sum(data.urlcount)
		st.subheader("**%s's total messages 💬**"% option)
		st.markdown(total_messages)
		st.subheader("**%s's total media 🎬**"% option)
		st.markdown(media_messages)
		st.subheader("**%s's total emojis 😂**"% option)
		st.markdown(emojis)
		st.subheader("**%s's total links**"% option)
		st.markdown(links)
		media_messages_df = data[(data['Message'] == ' <Media omitted>')|(data['Message'] == ' image omitted')|(data['Message'] == ' video omitted')|(data['Message'] == ' sticker omitted')]
		messages_df = data.drop(media_messages_df.index)
		messages_df = messages_df.drop(deleted_messages.index)
		messages_df = messages_df.drop(link_messages.index)
		messages_df['Letter_Count'] = messages_df['Message'].apply(lambda s : len(s))
		messages_df['Word_Count'] = messages_df['Message'].apply(lambda s : len(s.split(' ')))
		messages_df["MessageCount"]=1
		messages_df["emojicount"]= messages_df['emoji'].str.len()
		st.header("**Some more Stats**")
		st.subheader("**%s's emoji distribution 😂**"% option)
		st.text("Hover on Chart to see details.")
		st.plotly_chart(visualize_emoji(data),use_container_width=True)
		st.subheader("**%s's messages as Time moves on**"% option)
		st.text("Hover on Chart to see details.")
		st.plotly_chart(messages_as_time_moves_on(messages_df),use_container_width=True)
		st.subheader("**When is %s most active?**"% option)
		time_active(messages_df)
		st.pyplot()
		time.sleep(0.2)
		st.subheader("**The most happening day for %s was - **"% option)
		day(messages_df)
		st.pyplot()
		time.sleep(0.2)
		st.subheader("** %s's WordCloud **"% option)
		words(messages_df)
		st.pyplot()







		




# st.subheader('Number of pickups by hour')
# hist_values = np.histogram(data[DATE_COLUMN].dt.hour, bins=24, range=(0,24))[0]
# st.bar_chart(hist_values)

# # Some number in the range 0-23
# hour_to_filter = st.slider('hour', 0, 23, 17)
# filtered_data = data[data[DATE_COLUMN].dt.hour == hour_to_filter]

# st.subheader('Map of all pickups at %s:00' % hour_to_filter)
# st.map(filtered_data)