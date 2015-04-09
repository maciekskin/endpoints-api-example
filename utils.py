import base64
import json
import hmac
from Crypto.Hash import SHA256

import endpoints

SECRET_KEY = '46de1bd0ac720d3b1cc086ae70b657e589b63132c653e990025a8ad61b846ea6'


def base64url_decode(input):
    rem = len(input) % 4
    if rem > 0:
        input += b'=' * (4 - rem)
    return base64.urlsafe_b64decode(input)


def base64url_encode(input):
    return base64.urlsafe_b64encode(input).replace(b'=', b'')


def sha256_encode(key, message):
    return hmac.new(key, message, SHA256).hexdigest()


class JWTHelper(object):
    @staticmethod
    def get_jwt_token(payload):
        segments = []
        header = {'typ': 'JWT', 'alg': 'HS256'}

        json_header = json.dumps(
            header,
            separators=(',', ':'),
        ).encode('utf-8')

        segments.append(base64url_encode(json_header))

        json_payload = json.dumps(
            payload,
            separators=(',', ':'),
        ).encode('utf-8')

        segments.append(base64url_encode(json_payload))

        signing_input = b'.'.join(segments)

        signature = sha256_encode(SECRET_KEY, signing_input)

        segments.append(base64url_encode(signature))

        return b'.'.join(segments)

    @classmethod
    def validate_jwt_token(cls, token):
        try:
            payload, signing_input, header, signature = cls._load_jwt(token)
        except ValueError:
            raise endpoints.UnauthorizedException('Invalid token.')
        if not cls._verify_signature(payload, signing_input,
                                     header, signature):
            raise endpoints.UnauthorizedException('Invalid token.')
        return payload

    @classmethod
    def _verify_signature(cls, payload, signing_input, header, signature):
        valid_sign = sha256_encode(SECRET_KEY, signing_input)
        return hmac.compare_digest(signature, valid_sign)

    @classmethod
    def _load_jwt(cls, token):
        signing_input, crypto_segment = token.rsplit(b'.', 1)
        header_segment, payload_segment = signing_input.split(b'.', 1)
        header_data = base64url_decode(header_segment)
        header = json.loads(header_data.decode('utf-8'))
        payload_data = base64url_decode(payload_segment)
        payload = json.loads(payload_data.decode('utf-8'))
        signature = base64url_decode(crypto_segment)
        return (payload, signing_input, header, signature)
