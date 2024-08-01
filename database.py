"""
Provides the database schema, handles entity creation and record management
"""

from sqlalchemy import create_engine, Column, String, ForeignKey, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Article(Base):
    """
    Represents an article posted on a page
    """

    __tablename__ = 'article'
    id = Column(Integer, primary_key=True, autoincrement=True)
    text = Column(String)

class Image(Base):
    """
    Represents an image in an article
    """

    __tablename__ = 'image'
    id = Column(Integer, primary_key=True, autoincrement=True)
    article = Column(Integer, ForeignKey('article.id'))
    src = Column(String)

class Database:
    """
    Represents and manages the database engine connection
    """

    def __init__(self, uri='sqlite:///data.db'):
        self.engine = create_engine(uri)
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)

    def get_session(self):
        """
        Returns the database session
        """

        return self.session()

    def get_unsaved_articles(self, articles):
        """
        Returns a list of articles that isn't saved on the db

        This approach is not the best, comparing text can result in some inconsistencies
        but facebook makes it almost impossible to get the datetime the article was posted.
        They use a mix of canvas and svgs to render it (its rendered randomly), and there
        are dummy values mixed in to make it even harder to parse
        """

        if not articles or len(articles) < 1:
            return []

        unread_articles = []
        for article in articles:
            res = self.session().query(Article).filter_by(text=article.text).first()

            if not res:
                unread_articles.append(article)

        return unread_articles


db = Database()
