"""
Provides the database schema, handles entity creation and record management
"""

import os
from sqlalchemy import create_engine, delete, Column, String, ForeignKey, Integer
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

    def __init__(self, uri = None):
        if uri is None:
            # Ensure the directory exists
            directory = "data"
            if not os.path.exists(directory):
                os.makedirs(directory)
            uri = f"sqlite:///{directory}/data.db"

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

        session = self.get_session()

        unread_articles = []
        for article in articles:
            res = session.query(Article).filter_by(text=article['text']).first()

            if not res:
                unread_articles.append(article)

        session.close()
        return unread_articles

    def replace_existing_articles(self, articles):
        """
        Replaces the existing article records in the database
        with the new ones
        """

        # Dont delete old data if there is no new one
        if not articles or len(articles) < 1:
            return

        session = self.get_session()

        # Remove old data
        session.execute(delete(Article))
        session.execute(delete(Image))

        for article in articles:
            # Add the new article
            new_article = Article(text=article['text'])
            session.add(new_article)
            session.commit()

            # Add article's images
            for image in article['images']:
                new_image = Image(src=image, article=new_article.id)
                session.add(new_image)
                session.commit()

        session.close()

db = Database()
