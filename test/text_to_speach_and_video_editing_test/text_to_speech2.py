import pyttsx3
engine = pyttsx3.init()

# text = "在這場台中老鼠會「無卡分期」詐騙風波中，逢甲大學成為受害者的主戰場，不少學生被騙得血本無歸。一位受害者在網上大發牢騷，強調自己並非短視近利，只是相信朋友，結果被狡詐業者一筆擦去5000元。他描述當時的詐騙過程，揭示了詐騙集團高超的話術和手法。網友紛紛安慰受害者，但也有人冷嘲熱諷，認為被騙的人其實就是貪念驅使，這場「無卡分期」詐騙風波，看來是一出現代版的社會悲劇對啊。"
# engine.say(text)
text = "哈囉你好嗎?衷心感謝"
voices = engine.getProperty("voices")

for voice in voices:
    print(voice)
    engine.setProperty("voice", voice.id)
    engine.say(text)
    engine.runAndWait()
    # engine.save_to_file(text, "voice2.mp3")
