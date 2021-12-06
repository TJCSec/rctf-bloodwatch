import time
import urllib
import logging

import click
from click_loglevel import LogLevel
from discord_webhook import DiscordWebhook

import rctf

@click.command()
@click.option('-u', '--rctf-url', help='rCTF instance to monitor', required=True)
@click.option('-t', '--token', envvar='RCTF_TOKEN', help='rCTF token', required=True)
@click.option('-w', '--discord-webhook', envvar='DISCORD_WEBHOOK', help='Discord webhook', required=True)
@click.option('-i', '--interval', default=60, help='Seconds between checks', required=True)
@click.option('-d', '--division', multiple=True, help='Division(s) to include')
@click.option('-l', '--log-level', type=LogLevel(), default=logging.INFO, help='Log level', required=True)
def main(rctf_url, token, discord_webhook, interval, division, log_level):
  logging.basicConfig(level=log_level)

  client = rctf.RCTFClient(rctf_url, token)
  config = client.config()
  for d in division:
    if d not in config['divisions']:
      raise ValueError(f'invalid division {d}')
  divisions = set(division)

  def get_blooder(challenge):
    if challenge['solves'] == 0:
      return None
    i = 0
    while (solves := client.get_solves(challenge['id'], limit=10, offset=i * 10)['solves']):
      for solve in solves:
        if not divisions or client.public_profile(solve['userId'])['division'] in divisions:
          logging.debug(f'Challenge {challenge["name"]} ({challenge["id"]}) blooded by {solve["userName"]} ({solve["userId"]})')
          return solve
      i += 1

  def notify(challenge, blooder):
    userId = blooder['userId']
    userName = blooder['userName']
    url = urllib.parse.urljoin(client.url, f'/profile/{userId}')
    challName = challenge['name']
    logging.info(f'Notifying for {challName} ({challenge["id"]})')
    msg = f'Congratulations to [`{userName}`](<{url}>) for first blood on `{challName}`!'
    webhook = DiscordWebhook(url=discord_webhook, content=msg, allowed_mentions={'parse': []})
    webhook.execute()

  logging.info('Loading solved challenges')
  blooded = set()
  for challenge in client.get_challenges():
    logging.debug(f'Checking {challenge["name"]} ({challenge["id"]})')
    if get_blooder(challenge) is not None:
      blooded.add(challenge['id'])
  logging.info(f'Loaded {len(blooded)} solved challenges')

  while True:
    logging.debug(f'Sleeping for {interval} seconds')
    time.sleep(interval)
    logging.info('Checking for first bloods')
    for challenge in client.get_challenges():
      if challenge['id'] in blooded:
        logging.debug(f'Skipping {challenge["name"]} ({challenge["id"]})')
        continue
      logging.debug(f'Checking {challenge["name"]} ({challenge["id"]})')
      if (blooder := get_blooder(challenge)) is not None:
        notify(challenge, blooder)
        blooded.add(challenge['id'])

if __name__ == '__main__': main()