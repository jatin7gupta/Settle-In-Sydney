from alchemy import Session
from flask import Blueprint, request
from flask_restplus import Namespace, fields, Resource
from werkzeug.exceptions import NotFound, BadRequest
from tahelka.auth.token_authenticator import TokenAuthenticator
from tahelka.insight.crime_ranker import CrimeRanker
from tahelka.analytics.recorder import Recorder
from tahelka.util.util import limitCheck

api = Namespace('crime_rankings')
parser = api.parser()
parser.add_argument('limit', type=int, help='Limit the results to this amount.')
parser.add_argument('order', type=str, help='The order of the ranking (ascending/descending).')

@api.route('')
class CrimeRankings(Resource):
    @api.doc(description="Show list of Crime Ranks.")
    @api.param('limit', description='Limit the results to this amount.')
    @api.param('order', description='The order of the ranking (ascending/descending).')
    @api.expect(parser)
    @api.response(200, "Crime Ranking Successfully Displayed.")
    @api.response(400, "Invalid limit value entered")
    @api.response(401, "The credentials are incorrect.")
    def get(self):
        auth_header = request.headers.get('Authorization')
        TokenAuthenticator(auth_header, False).authenticate()

        limit = request.args.get('limit', 5)
        order = str(request.args.get('order', 'ascending'))

        order = order == "ascending"    #order is true for ascending, false otherwise

        limit = limitCheck(limit)

        data = CrimeRanker(limit, order).rank()

        status_code = 200
        record = Recorder('crime_rankings', status_code)
        record.recordUsage()

        resp = {'data' : data }
        return resp, status_code
