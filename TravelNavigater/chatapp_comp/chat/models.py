from django.db import models


# テーブルを作成
class Message(models.Model):
    contents = models.CharField(max_length=80)
    response = models.TextField()
    videoId_1 = models.CharField(max_length=80)
    url_1 = models.CharField(max_length=80)
    title_1 = models.CharField(max_length=80)
    thumbnails_1 = models.CharField(max_length=80)
    videoId_2 = models.CharField(max_length=80)
    url_2 = models.CharField(max_length=80)
    title_2 = models.CharField(max_length=80)
    thumbnails_2 = models.CharField(max_length=80)
    videoId_3 = models.CharField(max_length=80)
    url_3 = models.CharField(max_length=80)
    title_3 = models.CharField(max_length=80)
    thumbnails_3 = models.CharField(max_length=80)
    created_at = models.DateTimeField()

    # モデルを表すものとして、contents（書き込み内容）を使う
    def __str__(self):
        return self.contents


class Answer(models.Model):
    departure = models.CharField(max_length=80)
    destination = models.CharField(max_length=80)
    stay = models.CharField(max_length=80)
    created_at = models.DateTimeField()

    def __str__(self):
        return str(self.created_at)
