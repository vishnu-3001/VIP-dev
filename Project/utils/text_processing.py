import fitz
import openai

def extract_headings(path:str):
    headings=[]
    fonts_used=set()
    pdf_document=fitz.open(path)
    for page_number in range(len(pdf_document)):
        page=pdf_document[page_number]
        blocks=page.get_text("dict")["blocks"]
        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        fonts_used.add(span["font"])
                        if span["size"]>12:
                            text=span["text"]
                            if len(text)>0:
                                headings.append(text)
    pdf_document.close()
    return headings










def textReturn():
    return """I remember the date well: 4 March 2006. I was in Kolkata and about to reach Happy’s home. I had been very excited all morning as I was going to see our gang of four after three years. After our engineering, this was the first time when all of us—Manpreet, Amardeep, Happy and I—were going to be together. During our first year in the hostel, Happy and I were in different rooms on the fourth floor of the Block-A building. Being on the same floor, we were acquaintances but I never wanted to interact with him. I didn’t think him to be ‘a good guy’ because of his fondness for fights and the red on his mark sheet. But, unfortunately, I was late in getting back to the hostel at the beginning of the second year and almost all the rooms were already allotted by then. I was not left with any choice other than becoming Happy’s roommate. And because life is weird, things changed dramatically and, soon, we became the best of buddies. The day our reunion was scheduled, he had been working with TCS for two years and was enjoying his onsite project in London. Happy was blessed with a height of 6’1”, a good physique and stunning looks. 
And Happy was always happy. Manpreet, or MP as we called him, is short-statured, fair and healthy. 
The reason I use the word ‘healthy’ is because he will kill me if I use the proper word—‘fat’—for him. He was the first among us to get a computer in the hostel and his machine was home to countless computer games. In fact, this was the very reason Happy and I wanted to be friends with him. MP was quite studious. He had even cracked the Maths Olympiad in his school days, and was always boasting about it. His native place was Modinagar but, at the time of this reunion, he was working with Ocwen in Bangalore. 
Amardeep has been baptized ‘Raamji’ by MP. I don’t know when he got this weird nickname or why, but it was probably because of his simple, sober nature. Unlike the rest of us at the hostel, he was not at all a night person and his room’s light would go off precisely at 11 p.m. At times, MP, Happy and I used to stand outside his room a few seconds before 11 and begin to count down, ‘10, 9, 8, 7, 6, 5, 4, 3, 2, 1 … and Raamji has gone down.’ The only mysterious thing about Amardeep was that he used to go somewhere on his bicycle, every Sunday. He never told us where he went. Whenever we tried to follow him, somehow he would know and would digress from his path to shake us off. Even today, none of us knows anything about it. The best thing about the guy, though, is his simplicity. And, very importantly, he was the topper in the final semester of our Engineering batch. He made our group shine. He belonged to Bareilly and was working with Evalueserve when he, along with MP, flew to Kolkata for the reunion. 
After college, all of us were pretty much involved in our stereotypical lives. One day, we found out that Happy was coming back from London for two weeks. Everybody was game for a reunion. ‘Happy’s place in Kolkata, 4 March 2006,’ we decided. 
Finally, on the scheduled date, I was climbing the stairs to Happy’s apartment two steps at a time. It was about 12.30 in the afternoon when I knocked on his door. His mom opened it and welcomed me in.
As I had often been there, she knew me well. For me, Happy’s house never meant too many formalities. I was having some water when she told me that Happy was not at home and his cell was switched off. 
‘Wow! And he asked me not to be late,’ I murmured to myself. 
A little later, there was another knock on the door. I got up from my chair to open it, as Happy’s mom was in the kitchen. I pulled it open to shouts of, ‘Oh … Burrraaaaahhhh … Dude … Yeah … Huhaaaaaaaaa … Ohaaaaaaaaaa!’ 
No, it wasn’t Happy. MP and Amardeep had arrived. 
Seeing your college friends after three years is so crazy and exciting that you don’t even realize you are at someone else’s place where you should show some manners and be polite. Then again, the very purpose of this reunion was to recall our college days and this was the perfect start. While we made ourselves comfortable on the sofas in the drawing-room, MP asked about Happy’s whereabouts. 
‘He’s not on time in his own home,’ I said looking at MP and we laughed again. For the next half hour or so, the three of us talked, laughed and made fun of each other while eating lunch made by Happy’s mother. Yes, we started our meal without Happy. This might not sound decent, but we had genuine reason—nobody could predict his arrival, so there was no point in waiting. A little later, there was another knock. Happy’s mom opened the door. 
‘Happy veeeeeeeer!’ MP shouted, getting up from the dining chair. 
Amardeep and I stared at each other. It seemed as if MP was going to shed tears as he hugged Happy. We remembered how these guys used to cry during their long boozing sessions, when their brains switched off and their hearts started speaking. Amardeep and I used to enjoy our Coke, while seeing them getting senti. 
We all stood up to hug him and as soon as that was done, we continued our lunch. Happy also joined us. The food that day was very tasty. Or maybe it was just because we were having lunch together after so long and that made it special. 
After lunch, we moved to another flat, a few floors above, in the same building. This was the second flat which Happy’s family owned, and was meant for relatives and friends like us. We were laughing at one of MP’s jokes while moving in, and were probably still laughing as we fell on the giant couch in the drawing room—upside down—legs on the couch and our torsos on the floor, arms spread across and facing the ceiling; we made ourselves comfortable. 
Nobody said anything for a few moments. And then it started again with Happy’s big laugh. I guess he remembered some incident involving Raamji. 
That evening, the four of us in that flat were having an amazing time. Talking about our past and present. About those not-so-goodlooking girls in college. About the porn we used to watch on our computer. About our experiences abroad and many other things. 
‘So which one did you like more, Europe or the States?’ Happy asked me, getting up. ‘Europe,’ I replied, still lying down and looking at the ceiling. 
‘Why?’ Amardeep asked. He always needed to find out the reason behind everything (though he never gave any reason for not telling us where he went every Sunday, during our hostel days). ‘Europe has a history. The languages change when you leave one country and move to another. The food, the art and architecture, fabulous public transport, the scenic beauty, everything is just
wonderful in Europe,’ I tried to explain. 
‘You did not see all this in the US?’ 
‘Some things, like public transport, are not that good in comparison to Europe. You and your car are the only options in most of the states, New York being an exception. You won’t hear as many languages as you get to hear in Europe. I mean the US is damn advanced but still, I would prefer Europe to the States.’ 
Amardeep nodded and this meant his questions had ended. 
‘This is the best thing about IT jobs, Amardeep. We get to visit different places which we never dreamt of during our college days,’ MP said to Amardeep. After college MP, Happy and I joined IT firms, while Amardeep joined the KPO industry. He had never liked the hardcore software business. 
We were glad to be together again, finally, after the farewell night in college and we kept talking for hours that afternoon. We were planning an outing for the evening when we realized how tired we were and how badly we needed a little rest … I don’t remember which one of us fell asleep first, that afternoon. 
‘Wake up, you asses. It’s already 6.30.’ 
Someone was struggling to get us out from our utopia of dreams. In the hostel, Amardeep was the first among us to wake up and, of course, the only one to wake up others. So we knew that it was our early-morning Amardeep. 
Still, how can somebody thumping your door to get you out of bed be pleasant? We human beings have such a weird nature—while asleep, we hate the person who is trying to wake us up, but once we are awake, we tend to love that same person because he did the right thing. As usual, Amardeep was successful in his endeavor. It was 7 in the evening. 
This was the first time Amardeep and MP had come to the city, so we decided to explore the streets of Kolkata. Fortunately our host possessed two bikes—his own Pulsar and his younger brother’s Splendor. We got ready and pulled out the bikes from the garage. MP and I got on the Splendor, Happy and Amardeep on the Pulsar. 
We crossed the river Hooghly, over the Vidya Sagar Setu, shouting and talking to each other. Speed-breakers couldn’t break our speed that evening. And where were we? On cloud number nine. Being with your best buddies after such a long time is, at once, sentimental and thrilling. 
We went to the Victoria Memorial and few other places. At times, we got down to have some fruit juice. At times, we halted to enjoy Kolkata’s famous snacks and sweets. At times, we got down because one of us wanted to pee—which initiated a chain-reaction among the rest of us. 
We were at some place, enjoying ice-tea in an earthen cup, when MP asked, ‘When do we need to get back home?’ It was already 10.30. 
‘No worries. I have the keys for the flat upstairs. We can go any time we want. Hopefully, we will not move in before 1,’ Happy said, finishing his ice-tea down to the last drop. ‘And where are we going to be till then?’ Amardeep was concerned. 
Amardeep and his 11 p.m. sleeping time, I remembered, but didn’t bring it to the others’ notice. Happy looked at me and asked with a smile, ‘Shall we go to the same place?’ 
‘Oh! That one …?’ Before MP’s dirty brain-cells could start thinking something filthy, I tried to clear the picture. ‘Gentlemen! We are going to a very cool place now, and I bet both of you will find it
…’ 
I was trying to finish when MP became impatient and cut me off, ‘Oh yes. I heard that Chandramukhi was from West Bengal. So, are we guys planning to …?’ His wicked smile and naughty eyes completed the question. 
‘You’re nuts,’ Happy said, laughing. 
‘Don’t think too much, MP. Just follow us,’ I added. 
Without revealing any more, we were back on our bikes, driving to our destination. It wasn’t yet midnight when we reached the place. The air here was a little colder. At first glance it looked as if we were in the slums. There was a run-down garage which was shuttered. Some trucks were parked outside. Their drivers were probably sleeping. We parked our bikes beside one of the trucks and walked through a small street to the right of the garage. The place was badly lit and utterly silent. Our voices and footsteps rang out loudly. The sounds of insects added to the eeriness of the place. MP heard a pack of dogs barking somewhere nearby. I don’t know if he really heard them, though. Maybe it was just his poor heart, beating loudly. 
‘Shhh! They will wake up,’ said Happy with a finger on his lips. 
‘Who?’ Amardeep whispered. 
‘There are people sleeping on the ground ahead. Watch your step,’ Happy said. ‘People! Sleeping on the road?’ Amardeep slowed down. They were local fishermen. Some were sleeping and some were hung-over from home-made liquor. 
Suddenly, the street ended in a wooden channel. This was a staircase-like structure going down, and we could hear a dull sound, like that of water beating against the shore. We stepped on this channel leaving behind the insect-sounds. 
In a few seconds, we were at our destination. 
It was the river Hooghly, and we were standing at its bay. Amardeep’s and MP’s fear turned into delight. 
‘This is the Launch Ghat and, right now, we are in Howrah. This is the point from where the ferry takes you to the other side: Kolkata city,’ Happy announced, pointing across the river. In our excitement, we jumped onto the wooden harbor-like structure, from the channel. Surrounding this harbor on three sides was the river in its perfect velocity. It was a beautiful night, with the moon overhead and the stars shining bright. And beneath this sky, the four of us! 
We sat down beside one of the giant anchors in a corner of the harbor. The river raced against the cool breeze to meet the Bay of Bengal. In the silence, the sound of water hitting the harbor was crystal clear. On the other side of the river was Kolkata. The tall buildings and the chain of tiny, yellow lights 
reminded me of the New York skyline. But this was much better, just because I was with my friends now. 
With our arms wide open, we breathed deep and long, inhaling the fresh, chill air, still intoxicated by the beauty of this place. That was when Happy spoke up. 
‘So?’ he asked, looking at Amardeep. 
‘What?’ Amardeep asked in return, not understanding Happy’s ‘So.’ 
‘So, how is this place, dammit?’ 
‘Oh! This place? I cannot think of a better place than this. This is heaven.’
And then, again, a cool breeze blew, embracing us. We lay down on the harbor. That was when the discussion started. A serious discussion; a discussion that changed my life. It started with another ‘So’. 
‘So?’ Amardeep asked this time, looking at Happy. 
‘What?’ Happy asked, raising his chin. 
‘What’s the next important thing?’ Amardeep asked. 
‘You mean dinner?’ MP jumped in. 
‘No, I mean the next important thing in life. Schooling—done. Engineering—done. Getting a good job—done. Going abroad—done. Bank balance—in progress. What’s the next milestone?’ ‘Ah! I know what you’re talking about,’ Happy nodded. ‘Ask him,’ he said, pointing his already raised chin towards me. 
Everyone looked at me. 
‘I don’t know what’s going on in your life and family, but my mom and dad are going crazy. They’re after me like you wouldn’t believe. Don’t I make a good bachelor?’ I said. ‘The story is the same everywhere. We poor bachelors,’ MP said trying to be funny. ‘I am serious, MP,’ Amardeep said. 
‘So, have you or your family fixed something?’ I asked him. 
‘No. My story is just like yours. But the fact is that, one day, we’ll have to settle down with a life partner. How long can we ignore our parents’ questions? They too have expectations, wishes and dreams for us.’ 
‘I know what you mean Amardeep. But are you really ready to spend your whole life with someone? I mean, in our four years at the hostel, there were so many times when we had to adjust with each other … This one will be for a lifetime,’ Happy said. 
‘But, sooner or later, we have to do this, right?’ Amardeep asked. 
‘What if we just carry on the way we are?’ MP said. 
‘Then imagine yourself at the age of sixty, living alone. Life isn’t that easy, my friend. It’s a journey. And the best way to complete it is with a life-partner,’ Amardeep said. That night, on the bank of the river, the four of us discussed this issue seriously, for the first time. Maybe it was the first time we felt we were mature enough to talk about it. So many questions, ifs and buts were raised and answered between us. So many views were brought in and debated. None of us was against marriage but we wanted to evaluate its benefits. Amardeep and I were quite convinced about the marriage thing. And this discussion made Happy and MP think about the matter quite seriously, even it didn’t convince them. (Which reminds me of a slogan I read on a T-shirt: If you can’t convince her, just confuse her!) 
‘But then, other things come into the picture. Love marriage or arranged marriage? Parents’ choice or ours?’ Happy said. 
‘Now, that’s a personal choice. But given that we are independent, I don’t think our parents will object to our decision,’ Amardeep said. 
Happy kept mum hearing this. 
‘But Amardeep, look at our lives. All of us are North Indians, working in far-away states. The chance of finding a soul-mate, in this case, is quite slim. Moreover, the kinds of jobs we have don’t
give us the time to interact with different people. And above all, none of us would like to marry a girl chosen by our parents, if I am not wrong,’ MP said. 
‘I don’t know if your last statement is valid or not, but the rest is in your hands,’ Amardeep replied. ‘But MP has a point. In my case, I would like to marry a girl of my choice, but for the last one year I was abroad and I don’t know if, in the next couple of years, I will be in India. Given this fact, it is quite hard for me to work on my marriage plan. And for a person like me it’s impossible to settle down with any girl who is not Indian. Forget Indian, she has to be a Punjabi first of all,’ I said. ‘How did you apply for your job at Infosys?’ Amardeep asked, digressing from the topic. I answered, ‘Through some job website.’ 
‘And Happy, how did you transfer money from London to your parents?’ 
‘Through my Internet banking account. It’s quite fast,’ he answered. 
‘See? The world is becoming Internet-savvy. And, given the fact that we all are IT graduates who are on the net almost everyday, why can’t we use this for the marriage thing too?’ ‘Are you talking about matrimonial websites like Shaadi. com?’ Happy asked. ‘Yes.’ 
‘Are they really useful? I don’t think so,’ MP put forward his view. ‘To know if a dish is sweet or salty, you have to taste it first. That’s the only way to know things for sure,’ Amardeep answered. ‘Or better yet, ask a person who has already tasted it. Why take a chance?’ Happy said, trying to make us laugh. 
‘So Raamji, are you on any such website?’ I asked. 
‘Not yet. But I’m thinking of it …’ 
When we did not say anything, he explained, ‘The best thing about this service is that you can go through so many profiles without leaving your desk. The filters are good enough to provide you suitable matches. And you can interact with the persons who interest you … Everything is so systematic. Above all, you don’t need to worry about your physical location …’ 
Amardeep made some valid points, which is probably why we didn’t have much to debate about. ‘Hmm … Well, I don’t know if this thing is going to work, but it is worth giving a try. Who knows …?’ Even MP was convinced. 
It was 1.30 a.m. Our empty stomachs reminded our brains of their existence. 
Amardeep said, ‘It’s quite late and I’m damn hungry. Let’s get home.’ And he stood up stretching his back. 
‘So who’s the first one?’ MP asked while we all were dusting our clothes. 
‘The first one to marry? Or first one to make his profile on the website?’ Happy asked, laughing. ‘Both.’ 
‘I think this guy,’ Happy pointed his finger at me, I don’t know why. 
It was probably 4 a.m. by the time we had dinner and slept. And, after a long time, we enjoyed the kind of sleep we used to enjoy in our hostel. That day became one of the most memorable days in our lives. 
We spent the next day visiting some of the best hangouts in Kolkata. And we went again to the Launch Ghat in the evening to ride the ferry to the other side of the city. And, believe you me, being on the ferry was no less amazing than boarding the Titanic in 1912. Being with your best friends is
simply wonderful. We ate, drank, talked and enjoyed to the fullest at a pub called Some Place Else. That was the last night of the reunion trip. 
All three of them came to drop me at Howrah Station and, once again, the four of us hugged, just like we had at Hyderabad Station, on the last day of college. 
‘Who’s going to cry first?’ MP asked. But all of us laughed at that stupid and senti question. The train called me with its final whistle. I got into the carriage and stood at the door, waving to them all as the train left the platform. I reached Bhubaneswar the next morning. That same morning, Amardeep and MP boarded flights back to their respective places. Soon afterwards, Happy also flew back to London.
"""