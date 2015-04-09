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


"""ProtoRPC message class definitions for TvShows API."""


from protorpc import messages


class ListRequest(messages.Message):
    """ProtoRPC message definition to represent a TV Shows list query."""
    limit = messages.IntegerField(1, default=50)

    class Order(messages.Enum):
        NAME = 1
        RATE = 2
        DATE = 3
    order = messages.EnumField(Order, 2, default=Order.DATE)


class GetRequestMessage(messages.Message):
    """ProtoRPC message definition to represent a TV Show to be fetched."""
    id = messages.IntegerField(1, required=True)


class InsertRequestMessage(messages.Message):
    """ProtoRPC message definition to represent a TV Show to be inserted."""
    name = messages.StringField(1, required=True)
    rate = messages.IntegerField(2, required=True)


class TvShowResponseMessage(messages.Message):
    """ProtoRPC message definition to represent a TV Show that is stored."""
    id = messages.IntegerField(1)
    name = messages.StringField(2)
    rate = messages.IntegerField(3)
    date = messages.StringField(4)


class ListResponse(messages.Message):
    """ProtoRPC message definition to represent a list of stored TV Shows."""
    items = messages.MessageField(TvShowResponseMessage, 1, repeated=True)
