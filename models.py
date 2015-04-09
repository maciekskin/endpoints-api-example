# -*- coding: utf-8 -*-
# Copyright (C) 2010-2015 Maciej Skindzier, Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""Helper model class for TvShows Endpoints API.

Defines models for persisting and querying data on a per user basis and
provides a method for returning a 401 Unauthorized when no current user can be
determined.
"""

import hmac

import endpoints
from google.appengine.ext import ndb

from messages import TvShowResponseMessage
from utils import sha256_encode


SALT = '3fee87186b278c1d1c62d50ea9be011d89f050e619fc6abb0908e4168891356a'


class TvShow(ndb.Model):
    """Model to store TV Shows that have been inserted by users.
    """
    name = ndb.StringProperty(required=True)
    rate = ndb.IntegerProperty(required=True)
    date = ndb.DateTimeProperty(auto_now_add=True)
    user = ndb.StringProperty(required=False)

    @property
    def date_str(self):
        """Property to format a datetime object to string."""
        return self.date.strftime('%b %d, %Y %I:%M:%S %p')

    def to_message(self):
        """Turns the TvShow entity into a ProtoRPC object.

        This is necessary so the entity can be returned in an API request.

        Returns:
            An instance of TvShowsResponseMessage with the ID set to the
            datastore ID of the current entity, the name value
            and the date value equal to the string version of date
            from the property 'date_str'.
        """
        return TvShowResponseMessage(id=self.key.id(),
                                     name=self.name,
                                     rate=self.rate,
                                     date=self.date_str)

    @classmethod
    def put_from_message(cls, message, user_email):
        """Gets the current user and inserts a TV Show.

        Args:
            message: A TvShowRequestMessage instance to be inserted.

        Returns:
            The TV Show entity that was inserted.
        """
        current_user = User.get_current_user(user_email, check_password=False)
        entity = cls(name=message.name, rate=message.rate,
                     user=current_user.email)
        entity.put()
        return entity

    @classmethod
    def query_user(cls, user_email):
        """Creates a query for the TvShows of the current user.

        Returns:
            An ndb.Query object bound to the current user. This can be used
            to filter for other properties or order by them.
        """
        current_user = User.get_current_user(user_email, check_password=False)
        return cls.query(cls.user == current_user.email)


class User(ndb.Model):
    email = ndb.StringProperty(required=True)
    password = ndb.StringProperty(required=False)

    def validate_password(self, password):
        return hmac.compare_digest(self.password.encode('utf-8'),
                                   sha256_encode(SALT, password))

    def set_password(self, password):
        self.password = sha256_encode(SALT, password)

    @classmethod
    def put_from_message(cls, message):
        entity = cls(email=message.email)
        entity.set_password(message.password)
        entity.put()
        return entity

    @classmethod
    def get_current_user(cls, email, password='', check_password=True):
        entity = cls.query(cls.email == email).get()
        if not entity:
            raise endpoints.UnauthorizedException('User not found.')
        if check_password and not entity.validate_password(password):
            raise endpoints.UnauthorizedException('Invalid user or password.')
        return entity
