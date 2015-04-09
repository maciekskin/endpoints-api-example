'use strict';

var app = angular.module('TvShows', []);

app.controller('MainController', ['$scope', '$http', '$window', function ($scope, $http, $window) {
    var main = this;
    main.authorized = false;
    main.tvshows = [];
    main.tvshow = {};
    main.user = {};

    main.get_list = function(order) {
        order = order || 'DATE';
        $http({method: 'GET', url: '/_ah/api/tvshows/v1/tvshows?order='+order,
               headers: {'Authorization': 'Bearer ' + $window.sessionStorage.token}}).success(function(resp) {
                    main.tvshows = resp.data.items;
                }).error(function() {
                    alert('Error, cannot get list, please try again.');
                });
    }

    main.insert = function() {
        $http({method: 'POST', url: '/_ah/api/tvshows/v1/tvshows',
               data: main.tvshow,
               headers: {'Authorization': 'Bearer ' + $window.sessionStorage.token}}).success(function(resp) {
                    main.tvshow = {};
                    main.get_list();
                }).error(function() {
                    alert('Error, element not inserted, please try again.');
                });
    }

    main.signin = function() {
        $http({method: 'POST', url: '/_ah/api/tvshows/v1/users/login',
               data: main.user}).success(function(resp) {
                $window.sessionStorage.token = resp.data.token;
                main.user = {};
                main.authorized = true;
                main.get_list();
        }).error(function() {
            alert('Error, cannot log in, please try again.');
        });
    }

    main.signon = function() {
        $http({method: 'POST', url: '/_ah/api/tvshows/v1/users/register',
              data: main.user}).success(function(resp) {
                main.user = {};
                alert('Account created successfuly, please log in.');
        }).error(function() {
            alert('Error, account not created, please try again.');
        });
    }

    main.signout = function() {
        $window.sessionStorage.token = '';
        main.authorized = false;
        main.tvshows = {};
        main.tvshow = {};
    }
}]);
