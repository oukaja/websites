import uuid
from bidi.algorithm import get_display
import arabic_reshaper
import pymysql.cursors



class AppPipeline(object):

    def __init__(self):
        self.c = 0
        self.db = pymysql.connect(host="localhost",  # your host
                                  user="root",  # username
                                  passwd="",  # password
                                  db="data",  # name of the database
                                  charset='utf8mb4',
                                  cursorclass=pymysql.cursors.DictCursor)
        cursor = self.db.cursor()
        self.db.set_charset("utf8")
        cursor.execute('SET NAMES utf8;')
        cursor.execute('SET CHARACTER SET utf8;')
        cursor.execute('SET character_set_connection=utf8;')
        cursor.close()
        self.db.commit()

    def process_item(self, item, spider):
        i = dict(item)
        cursor = self.db.cursor()
        cursor.execute("SELECT id FROM article WHERE link=%s", (i["link"]))
        results = cursor.rowcount
        if results == 0:
            ida = uuid.uuid4().__str__()
            title = get_display(arabic_reshaper.reshape(u'' + i["title"])).replace("'", "")
            author = get_display(arabic_reshaper.reshape(u'' + i["author"])).replace("'", "")
            link = i["link"]
            description = get_display(arabic_reshaper.reshape(u'' + "\n".join(i["description"]))).replace("'", "")
            try:
                cursor.execute(query="INSERT INTO article(id, title, author, link, descrip) VALUES (%s,%s,%s,%s,%s)",
                               args=(ida, title, author, link, description))
            except Exception as e:
                print("########"+e)
            finally:
                self.db.commit()
                cursor.close()
            comments = i["comments"]
            l = len(comments)
            names = i["names"]
            feedbacks = i["feedbacks"]
            if len(feedbacks) == 0:
                feedbacks = ['0' for i in range(l)]
            else:
                feedbacks = ['0' if v is None else v for v in i["feedbacks"]]
            cursor = self.db.cursor()
            for comment, name, feedback in zip(comments, names, feedbacks):
                try:
                    cursor.execute(
                            query="INSERT INTO comments(id_article, comment, name, feedback) VALUES (%s,%s,%s,%s)",
                            args=(ida,
                                  get_display(arabic_reshaper.reshape(u'' + comment.replace("'", ""))),
                                  get_display(arabic_reshaper.reshape(u'' + name.replace("'", ""))),
                                  feedback
                                  )
                        )
                    self.db.commit()
                except Exception as e:
                    print("======="+e.__str__())
            cursor.close()
        else:
            idup = cursor.fetchone()
            cursor.execute("DELETE FROM comments WHERE id_article = %s", (idup['id']))
            self.db.commit()
            comments = i["comments"]
            l = len(comments)
            if l != 0:
                names = i["names"]
                feedbacks = i["feedbacks"]
                if len(feedbacks) == 0:
                    feedbacks = ['0' for i in range(l)]
                else:
                    feedbacks = ['0' if v is None else v for v in i["feedbacks"]]
                for comment, name, feedback in zip(comments, names, feedbacks):
                    try:
                        cursor.execute(
                            query="INSERT INTO comments(id_article, comment, name, feedback) VALUES (%s,%s,%s,%s)",
                            args=(idup['id'],
                                  get_display(arabic_reshaper.reshape(u'' + comment.replace("'", ""))),
                                  get_display(arabic_reshaper.reshape(u'' + name.replace("'", ""))),
                                  feedback
                                  )
                        )
                        self.db.commit()
                    except Exception as e:
                        print(e.__str__())
        cursor.close()

    def spider_closed(self, spider):
        self.db.close()
