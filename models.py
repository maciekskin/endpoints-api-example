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


import endpoints
from google.appengine.ext import ndb

from messages import TvShowResponseMessage


class TvShow(ndb.Model):
    """Model to store TV Shows that have been inserted by users.
    """
    name = ndb.StringProperty(required=True)
    rate = ndb.IntegerProperty(required=True)
    date = ndb.DateTimeProperty(auto_now_add=True)
    user = ndb.UserProperty(required=True)

    @property
    def date_str(self):
        """Property to format a datetime object to string."""
        return self.date.strftime('%b %d, %Y %I:%M:%S %p')

    def to_message(self):
        """Turns the TvShow entity into a ProtoRPC object.

        This is necessary so the entity can be returned in an API request.

        Returns:
            An instance of TvShowsResponseMessage with the ID set to the datastore
            ID of the current entity, the name simply the entity's name
            value and the date value equal to the string version of date
            from the property 'date_str'.
        """
        return TvShowResponseMessage(id=self.key.id(),
                                    name=self.name,
                                    rate=self.rate,
                                    date=self.date_str)

    @staticmethod
    def get_current_user():
        current_user = endpoints.get_current_user()
        if current_user is None:
            raise endpoints.UnauthorizedException('Invalid token.')
        return current_user

    @classmethod
    def put_from_message(cls, message):
        """Gets the current user and inserts a TV Show.

        Args:
            message: A TvShowRequestMessage instance to be inserted.

        Returns:
            The TV Show entity that was inserted.
        """
        current_user = cls.get_current_user()
        entity = cls(name=message.name, rate=message.rate,
                     user=current_user)
        entity.put()
        return entity

    @classmethod
    def query_current_user(cls):
        """Creates a query for the TvShows of the current user.

        Returns:
            An ndb.Query object bound to the current user. This can be used
            to filter for other properties or order by them.
        """
        current_user = cls.get_current_user()
        return cls.query(cls.user == current_user)
