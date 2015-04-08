'use strict';

var app = angular.module('TvShows', []);
var CLIENT_ID = '603902234563-lp0ujjsr874tcla49dpcqngahhc745vo.apps.googleusercontent.com';
var SCOPES = ['https://www.googleapis.com/auth/userinfo.email'];

app.controller('MainController', ['$scope', '$window', function ($scope, $window) {
    var main = this;
    main.is_backend_ready = false;
    main.authorized = false;
    main.tvshows = [];
    main.tvshow = {};

    main.get_list = function() {
        gapi.client.tvshows.tvshows.list().execute(function(resp) {
            if (!resp.code) {
                $scope.$apply(function() {
                    main.tvshows = resp.items;
                });
            }
        });
    }

    main.insert = function() {
        gapi.client.tvshows.tvshows.insert(main.tvshow).execute(function(resp) {
            if (!resp.code) {
                $scope.$apply(function() {
                    main.tvshow = {};
                    main.get_list();
                });
            }
        });
    }

    main.signin = function(mode) {
        gapi.auth.authorize({client_id: CLIENT_ID,
            scope: SCOPES,
            immediate: mode},
            function() {
                gapi.client.oauth2.userinfo.get().execute(function(resp) {
                    if (!resp.code) {
                        $scope.$apply(function() {
                            main.authorized = true;
                            main.get_list();
                        });
                    }
                });
            });
    }
    
    main.signout = function() {
       gapi.auth.setToken(null);
       main.authorized = false; 
    }

    $scope.load_tvshows_lib = function() {
        var apisToLoad;
        var loadCallback = function() {
            if (--apisToLoad == 0) {
                $scope.$apply(function() {
                    main.is_backend_ready = true;
                    main.signin(true);
                });
            }
        };

        apisToLoad = 2;
        gapi.client.load('tvshows', 'v1', loadCallback, '//' + window.location.host + '/_ah/api');
        gapi.client.load('oauth2', 'v2', loadCallback);
    }

    $window.init = function() {
        $scope.$apply($scope.load_tvshows_lib);
    };

}]);

function init() {
    window.init();
}
