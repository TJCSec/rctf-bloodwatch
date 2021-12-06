import requests
import urllib

class APIError(Exception):
  def __init__(self, kind, message):
    self.kind = kind
    self.message = message
    super().__init__(self.message)

  def __str__(self):
    return f'{self.kind}: {self.message}'

class RCTFClient:
  def __init__(self, url, token=None):
    if not urllib.parse.urlparse(url).scheme in ['http', 'https']:
      raise ValueError(f'Invalid URL: {url}')
    self.url = url
    self.session = requests.Session()
    if token is not None:
      self.session.headers.update({'Authorization': f'Bearer {token}'})

  @staticmethod
  def _handleresponse(resp, valid, message=False):
    if resp['kind'] in valid:
      if message:
        return resp['message']
      return resp['data']
    raise APIError(resp['kind'], resp['message'])

  def _request(self, method, endpoint, **data):
    url = urllib.parse.urljoin(self.url, f'/api/v1{endpoint}')

    if data:
      data = {k: v for k, v in data.items() if v is not None}

    if method == 'GET' and data:
      resp = self.session.request(
        method, url,
        params=data,
      )
    else:
      resp = self.session.request(
        method, url,
        json=data,
      )
    return resp.json()

  def config(self):
    response = self._request('GET', '/integrations/client/config')
    return RCTFClient._handleresponse(response, ['goodClientConfig'])

  def login(self, token):
    response = self._request('POST', '/auth/login',
      teamToken=token,
    )
    self.token = RCTFClient._handleresponse(response, ['goodLogin'])['authToken']
    self.session.headers.update({'Authorization': f'Bearer {self.token}'})

  def get_challenges(self):
    response = self._request('GET', '/challs')
    return RCTFClient._handleresponse(response, ['goodChallenges'])

  def get_solves(self, chall, limit=10, offset=0):
    response = self._request('GET', f'/challs/{urllib.parse.quote(chall)}/solves',
      limit=limit,
      offset=offset,
    )
    return RCTFClient._handleresponse(response, ['goodChallengeSolves'])

  def submit_flag(self, chall, flag):
    response = self._request('POST', f'/challs/{urllib.parse.quote(chall)}/submit',
      flag=flag,
    )
    return RCTFClient._handleresponse(response, ['goodFlag'])

  def get_members(self):
    response = self._request('GET', '/users/me/members')
    return RCTFClient._handleresponse(response, ['goodMemberData'])

  def add_member(self, email):
    response = self._request('POST', '/users/me/members',
      email=email
    )
    return RCTFClient._handleresponse(response, ['goodMemberCreate'])

  def remove_member(self, member):
    response = self._request('DELETE', f'/users/me/members/{member}')
    return RCTFClient._handleresponse(response, ['goodMemberDelete'])

  def private_profile(self):
    response = self._request('GET', '/users/me')
    return RCTFClient._handleresponse(response, ['goodUserData'])

  def public_profile(self, uuid):
    response = self._request('GET', f'/users/{urllib.parse.quote(uuid)}')
    return RCTFClient._handleresponse(response, ['goodUserData'])

  def update_account(self, name=None, division=None):
    response = self._request('PATCH', '/users/me',
      name=name,
      division=division,
    )
    return RCTFClient._handleresponse(response, ['goodUserUpdate'])

  def update_email(self, email):
    response = self._request('PUT', '/users/me/auth/email',
      email=email,
    )
    return RCTFClient._handleresponse(response, ['goodVerifyEmailSent', 'goodEmailSet'], message=True)

  def delete_email(self):
    response = self._request('DELETE', '/users/me/auth/email')
    return RCTFClient._handleresponse(response, ['goodEmailRemoved', 'badEmailNoExists'], message=True)

  def get_scoreboard(self, division=None, limit=100, offset=0):
    response = self._request('GET', '/leaderboard/now',
      division=division,
      limit=limit,
      offset=offset,
    )
    return RCTFClient._handleresponse(response, ['goodLeaderboard'])

  def get_graph(self, division=None, limit=10):
    response = self._request('GET', '/leaderboard/graph',
      division=division,
      limit=limit,
    )
    return RCTFClient._handleresponse(response, ['goodLeaderboard'])
