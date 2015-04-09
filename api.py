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

import os

import endpoints
from protorpc import remote

from messages import (
    GetRequestMessage,
    InsertRequestMessage,
    ListRequest,
    ListResponse,
    TvShowResponseMessage,
    UserRequestMessage,
    RegisterResponseMessage,
    LoginResponseMessage
)
from models import TvShow, User
from utils import JWTHelper


@endpoints.api(name='tvshows',
               version='v1')
class TvShowsApi(remote.Service):
    """TvShows API v1"""

    @endpoints.method(GetRequestMessage, TvShowResponseMessage,
                      path='tvshows/{id}', http_method='GET',
                      name='tvshows.get')
    def tvshow_get(self, request):
        """Exposes an API endpoint to get a TV Show for the current user.

        Args:
            request: An instance of GetRequestMessage parsed from the API
                request.

        Returns:
            An instance of TvShowResponseMessage containing the TV Show,
            the name, the time the TV Show was inserted and the ID.
        """
        # TODO: validate if user owns tvshow?
        entity = TvShow.get_by_id(request.id)
        if not entity:
            raise endpoints.NotFoundException('TV Show %s not found.' %
                                              (request.id,))
        return entity.to_message()

    @endpoints.method(ListRequest, ListResponse,
                      path='tvshows', http_method='GET',
                      name='tvshows.list')
    def tvshows_list(self, request):
        """Exposes an API endpoint to query for TV Shows for the current user.

        Args:
            request: An instance of ListRequest parsed from the API
                request.

        Returns:
            An instance of TvShowsListResponse containing the TV Shows for the
            current user returned in the query. If the API request specifies an
            order of WHEN (the default), the results are ordered by time from
            most recent to least recent. If the API request specifies an order
            of NAME, the results are ordered by the name value of the TV Shows.
        """
        header = os.environ.get('HTTP_AUTHORIZATION', '')
        token = header.split(' ')[-1]
        payload = JWTHelper.validate_jwt_token(token)
        query = TvShow.query_user(payload['email'])
        if request.order == ListRequest.Order.NAME:
            query = query.order(TvShow.name)
        elif request.order == ListRequest.Order.RATE:
            query = query.order(-TvShow.rate)
        elif request.order == ListRequest.Order.DATE:
            query = query.order(-TvShow.date)
        items = [entity.to_message() for entity in query.fetch(request.limit)]
        return ListResponse(items=items)

    @endpoints.method(InsertRequestMessage, TvShowResponseMessage,
                      path='tvshows', http_method='POST',
                      name='tvshows.insert')
    def tvshows_insert(self, request):
        """Exposes an API endpoint to insert a TV Show for the current user.

        Args:
            request: An instance of TvShowRequestMessage parsed from the API
                request.

        Returns:
            An instance of TvShowResponseMessage containing inserted Show,
            the name, the time the TV Show was inserted and the ID.
        """
        header = os.environ.get('HTTP_AUTHORIZATION', '')
        token = header.split(' ')[-1]
        payload = JWTHelper.validate_jwt_token(token)
        entity = TvShow.put_from_message(request, payload['email'])
        return entity.to_message()

    @endpoints.method(UserRequestMessage, RegisterResponseMessage,
                      path='users/register', http_method='POST',
                      name='users.signon')
    def user_signon(self, request):
        """Exposes an API endpoint to insert new user.

        Args:
            request: An instance of UserRequestMessage parsed from the API
                request.

        Returns:
            An instance of UserResponseMessage containing new user email.
        """
        entity = User.put_from_message(request)
        return RegisterResponseMessage(email=entity.email)

    @endpoints.method(UserRequestMessage, LoginResponseMessage,
                      path='users/login', http_method='POST',
                      name='users.signin')
    def user_signin(self, request):
        """Exposes an API endpoint to insert new user.

        Args:
            request: An instance of UserRequestMessage parsed from the API
                request.

        Returns:
            An instance of LoginResponseMessage containing new user email
            and JWT token.
        """
        entity = User.get_current_user(request.email, request.password)
        payload = {'email': entity.email}
        token = JWTHelper.get_jwt_token(payload)
        return LoginResponseMessage(email=entity.email,
                                    token=token)


APPLICATION = endpoints.api_server([TvShowsApi])
