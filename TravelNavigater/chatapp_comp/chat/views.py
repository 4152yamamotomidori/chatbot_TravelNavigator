from django.shortcuts import render, redirect
from django.utils import timezone
import openai
import random
import json
import requests
from datetime import datetime
from .models import Message, Answer
from googleapiclient.discovery import build


def index(request): # 最初の画面、過去のMessage.objects(履歴)をhtmlに表示する
    messages = Message.objects.order_by('-created_at').reverse() # クエリセット（モデルのデータベースから取り出したデータ）を降順に並び替えて取得し変数へ代入
    context = {'messages': messages} # 辞書型へ

    # 朝、昼、夕方、夜に応じて背景を変更
    now = datetime.now()  # 現在時刻の取得
    hour = now.hour

    if 5 <= hour < 12:
        background_image = 'mountain08.png'
    elif 12 <= hour < 18:
        background_image = 'beach10.png'
    elif 18 <= hour < 22:
        background_image = 'hill_evening05.png'
    else:
        background_image = 'milkyway01.png'

    # 11行目で作成したcontext(辞書型)に結合
    context['background_image'] = f'../static/images/{background_image}'

    return render(request, 'chat/index.html', context) # return render(大抵request,表示させたいHTML,渡したい変数)


def post(request): # htmlのfromが入力されると、内容がpost関数へやってくる

    if request.method == "POST":
        if "departure" in request.POST:
            departure = request.POST['departure']
            destination = request.POST['destination']
            stay = request.POST['stay']
            question = f"{departure}から{destination}の、{stay}の旅行プランを提案してください。"

            Answer.objects.create(
                departure=departure,
                destination=destination,
                stay=stay,
                created_at=timezone.now()
                )
            youtube_api_keyword = f"{destination}　旅行"

        # 画面下のフリー入力フォーム
        elif "contents" in request.POST:
            contents = request.POST['contents']
            question = f"{contents}。"


        # ボタン
        elif "tourist_spot" in request.POST:
            last_answer=Answer.objects.order_by('created_at').last() # 最新のデータベースを取得
            question = f"{last_answer.destination}の観光地についてもっと詳しく教えてください。"
            youtube_api_keyword = f"{last_answer.destination}　観光地"

        elif "hotel" in request.POST:
            last_answer = Answer.objects.order_by('created_at').last()  # 最新のデータベースを取得
            question = f"{last_answer.destination}のホテルについてもっと詳しく教えてください。"
            youtube_api_keyword = f"{last_answer.destination}　ホテル"

        elif "gourmet" in request.POST:
            last_answer = Answer.objects.order_by('created_at').last()  # 最新のデータベースを取得
            question = f"{last_answer.destination}のグルメやおいしいレストランについてもっと詳しく教えてください。"
            youtube_api_keyword = f"{last_answer.destination}　グルメ"

        elif "souvenir" in request.POST:
            last_answer = Answer.objects.order_by('created_at').last()  # 最新のデータベースを取得
            question = f"{last_answer.destination}のお土産についてもっと詳しく教えてください。"
            youtube_api_keyword = f"{last_answer.destination}　お土産"

        elif "reset" in request.POST:
            question = "今までの会話をリセットしてください。"

# chatGPTAPI
    openai.api_key = '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'
# chatGPTからのレスポンスを代入
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "日本語で応答してください。あなたは旅行のモデルプランを作成するプランナーです。質問に対して返答する際、追加の情報を求めるような返答をしないでください。「さらに詳しく教えてください。」「具体的にどのような情報をお求めでしょうか？」等は禁止です。300文字以内で提案してください。" # 事前に細かい指示を入れる
            },
            {
                "role": "user", # ユーザーからの質問
                "content": question # chatGPTへの質問
            },
        ]
    )

# chatGPTからのレスポンス(辞書型)の中から必要なものを抜き出す
    results = response["choices"][0]["message"]["content"]


# youtubeAPI
    keyword = youtube_api_keyword
    YOUTUBE_API_KEY = 'AIzaSyDUS_a8AvIVIsGFPnVrHG-ipL50osrFCzk'

    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
    search_responses = youtube.search().list(
        q=keyword,
        part='snippet',
        type='video',
        regionCode="jp",
        maxResults=5, ).execute()
    # print(search_responses)

    # api取得結果からitemsのみ取り出し
    search_responses_items = search_responses['items']


    # モデルからオブジェクトを１つ作成し、データベースに保存
    Message.objects.create(
        contents=question,  # ユーザーの質問
        response=results,  # ChatGPTの返事
        videoId_1=search_responses_items[0]['id']['videoId'],
        url_1='https://www.youtube.com/watch?v=' + search_responses_items[0]['id']['videoId'],
        title_1=search_responses_items[0]['snippet']['title'],
        thumbnails_1=search_responses_items[0]['snippet']['thumbnails']['default']['url'],
        videoId_2=search_responses_items[1]['id']['videoId'],
        url_2='https://www.youtube.com/watch?v=' + search_responses_items[1]['id']['videoId'],
        title_2=search_responses_items[1]['snippet']['title'],
        thumbnails_2=search_responses_items[1]['snippet']['thumbnails']['default']['url'],
        videoId_3=search_responses_items[2]['id']['videoId'],
        url_3='https://www.youtube.com/watch?v=' + search_responses_items[2]['id']['videoId'],
        title_3=search_responses_items[2]['snippet']['title'],
        thumbnails_3=search_responses_items[2]['snippet']['thumbnails']['default']['url'],
        created_at=timezone.now(),
    )

    return redirect('chat:index') # index関数にリダイレクト


def lottery(request):
    destination_lottery = {"destination1": ""}  # 初期値を設定
    # くじの画像がクリックされたらここが動く
    if request.method == "POST":
        if "travel_lottery" in request.POST:
            lottery_list = ["北海道", "沖縄", "雲仙", "大阪", "金沢", "仙台", "有馬温泉", "別府", "ディズニー"]
            lottery_list_text = {"北海道": "北海道は驚くほど美しい自然が広がり、四季折々の風景が心を打つ。雄大な山々、清らかな湖沼、美味な海の幸が楽しめ、温泉や親しみやすい地元の人々が心地よい空間を作り出す。冬は雪景色が絶景で、冬スポーツも満喫。夏には花畑や青い空、美食が楽しめ、一生に一度の経験ができる場所。北海道は自然と食に溢れ、心に残る旅の思い出が待っている。",
                                 "沖縄": "沖縄は青い海と白い砂浜、温暖な気候が魅力。美しいサンゴ礁やカラフルな魚が広がる海での水中アドベンチャーは圧巻。沖縄料理の美味しさも魅力的で、島の文化や伝統に触れることで癒しと新しい発見が広がる。歴史的な遺産や美しい自然も訪れる価値あり。親しみやすい地元の人々との交流も旅を特別なものに。沖縄は穏やかな南国の楽園で、心に残る旅の思い出が待っています。",
                                 "雲仙": "雲仙は活火山横に広がる絶美な温泉地。噴火によるダイナミックな地形、温泉に浸かりながらの壮大な山並みが心を打つ。有明海の美しい夕景、歴史ある仙人の里も魅力。新緑、紅葉、雪景色と四季折々の風情が楽しめ、濃厚な温泉と豊かな自然が心身を癒す。美食も豊富で、親しみやすい地元の人々と触れ合いながら、雲仙は穏やかで贅沢な旅の場。",
                                 "大阪": "大阪は活気あふれるエネルギッシュな都市。美味なるグルメ天国であり、道頓堀のネオン輝くシンボルが賑やかな雰囲気を演出。歴史的な大阪城や新世界の観覧車も魅力。地元のおおらかな人々と触れ合いながら、独自の文化と笑いにあふれたエンターテイメントが待つ。近隣の奈良や京都へもアクセス良く、古都との対比も楽しめる。大阪は心躍る街で、食と笑い、歓迎の心に包まれる旅が楽しめる。",
                                 "金沢": "金沢は歴史と美意識が調和する宝石。兼六園の美しい庭園、金沢城の風格、料理の高級感が魅力。武家町の情緒ある街並みや伝統工芸の里、近代的な美術館も楽しめ、歩くたびに感動と発見が広がる。加賀友禅や能楽堂も見どころ。新鮮な海の幸、地元の食材を使った粋な味わいも楽しまれ、おしゃれなカフェや商店街での散策が心地よい。金沢は日本の美が詰まった穏やかで洗練された旅の場。",
                                 "仙台": "仙台は歴史とモダンが共鳴する都市。緑豊かな環境と静謐な仙台城、牛たんや伊達政宗ゆかりの名所が楽しめる。宮城の新鮮な海の幸や、地元産の美味な食材が豊富。世界的な芸術との交流が魅力のミヤコワスレ、夏の七夕や仙台藩政時代の風情も感じられる。温かな地元の人々と触れ合いながら、歴史と自然、美食とアートが融合した仙台で、心に残る旅の思い出が広がります。",
                                 "有馬温泉": "有馬温泉は歴史と癒しの名所。美しい山間の渓谷に佇み、金泉の湯と呼ばれる贅沢な温泉で極上のリラックス。日本最古の温泉地であり、雅な歴史的建築や庭園も堪能。四季折々の風情と美味なる料理が、心身を満たす。伝統的な文化体験や周辺の観光地も楽しめ、優雅なひとときが広がります。有馬温泉は、独自の魅力と静寂な癒しで、贅沢な温泉旅行の場として心を惹きつけます。",
                                 "別府": "別府は活気と癒しの共演。世界三大温泉地の一つで、多彩な湯と美肌効果が楽しめる。地獄めぐりでは地熱の迫力を感じ、美しい海と山に囲まれた自然も魅力。新鮮な海の幸や地元の食材が楽しめ、温泉街の歴史的な建築や文化も愉しい。伝統とモダンが調和し、親しみやすい地元の人々とのふれあいが心地よい。別府は五感で楽しむ総合リゾートで、活力とリラックスが満ちる旅の目的地です。",
                                 "ディズニー": "ディズニーは夢と魔法の王国。キャラクターとのふれあい、壮大なアトラクション、パレード、ショーが心躍る。カラフルな世界観、美しい建築、一流のエンターテイメントが広がり、家族や友達との特別な瞬間が生まれる。ディズニーのホスピタリティと笑顔に包まれ、幸せな気分が満ちる。夢と現実が交わる場所で、心に残る感動の体験が待っています。ディズニーは永遠の子ども心を呼び覚ます、魅力の詰まった魔法の場所です。"}

            random_destination = random.choice(lottery_list) # ランダムで行先を選ぶ
            b = f"{random_destination}がおすすめ"
            random_destination_text = lottery_list_text.get(random_destination) # ランダムで選ばれた行先の説明文
            destination_lottery = {"destination1": b}
            destination_lottery['destination_text'] = random_destination_text

            # ここから楽天トラベルapi、ランダムで選ばれた行先をキーワード検索。5件のホテルを取ってくる
            # アプリid
            app_id = "1041388673366341200"
            # リクエストurl
            url = "https://app.rakuten.co.jp/services/api/Travel/KeywordHotelSearch/20170426?"

            # params
            params = {"format": "json",
                      "keyword": random_destination,
                      "hits": "5",
                      "applicationId": app_id}

            # getメソッドでリクエスト、resにjson形式で代入
            response = requests.get(url, params)

            # 取得したデータを辞書型に変換
            res = json.loads(response.text)

            # きれいに見えるように
            # print(json.dumps(res, indent=2, ensure_ascii=False))

            # データの中からhotel情報のみ取り出す
            hotels_data = []
            for hotel_info in res['hotels']:
                for hotel_entry in hotel_info['hotel']:
                    hotel_basic_info = hotel_entry.get('hotelBasicInfo')
                    if hotel_basic_info:
                        hotels_data.append(hotel_basic_info)

                        destination_lottery['hotels_data'] = hotels_data
    return render(request, "chat/lottery.html", destination_lottery)
