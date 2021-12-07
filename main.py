import time
import logging

import click
from click_loglevel import LogLevel
from discord_webhook import DiscordWebhook

import rctf

@click.command(name='rctf-bloodwatch')
@click.option('-u', '--url', envvar='RCTF_URL', help='rCTF URL to monitor', required=True)
@click.option('-t', '--token', envvar='RCTF_TOKEN', help='rCTF API token', required=True)
@click.option('-d', '--division', multiple=True, envvar='RCTF_DIVISION', help='rCTF division(s) to include', show_default='all divisions')
@click.option('-w', '--discord-webhook', envvar='DISCORD_WEBHOOK', help='Discord webhook URL', required=True)
@click.option('-m', '--message', envvar='BLOOD_MESSAGE', help='Message to send to webhook', required=True)
@click.option('-i', '--interval', default=60, envvar='BLOOD_INTERVAL', help='Seconds between checks', show_default=True)
@click.option('-l', '--log-level', type=LogLevel(), default='INFO', envvar='LOG_LEVEL', help='Log level', show_default=True)
def main(url, token, discord_webhook, interval, message, division, log_level):
  logging.basicConfig(level=log_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
  logger = logging.getLogger('bloodwatch')

  client = rctf.RCTFClient(url, token)
  config = client.config()
  divisions = set()
  for d in division:
    if d not in config['divisions']:
      raise ValueError(f'invalid division {d}')
    divisions.add(d)

  def get_challenges():
    try:
      return client.get_challenges()
    except rctf.APIError as e:
      if e.kind == 'badNotStarted':
        logger.warn('CTF has not started yet')
        return []
      raise e

  def get_blooder(challenge):
    if challenge['solves'] == 0:
      return None
    i = 0
    while (solves := client.get_solves(challenge['id'], limit=10, offset=i * 10)['solves']):
      for solve in solves:
        if not divisions or client.public_profile(solve['userId'])['division'] in divisions:
          logger.debug(f'Challenge {challenge["name"]} ({challenge["id"]}) blooded by {solve["userName"]} ({solve["userId"]})')
          return solve
      i += 1

  def notify(challenge, blooder):
    logger.info(f'Notifying {challenge["name"]} ({challenge["id"]})')
    vars = {
      'challenge': challenge,
      'blooder': blooder,
    }
    content = message.format(**vars)
    webhook = DiscordWebhook(url=discord_webhook, content=content, allowed_mentions={'parse': []})
    return webhook.execute()

  logger.info('Loading solved challenges')
  blooded = set()
  for challenge in get_challenges():
    logger.debug(f'Checking {challenge["name"]} ({challenge["id"]})')
    if get_blooder(challenge) is not None:
      blooded.add(challenge['id'])
  logger.info(f'Loaded {len(blooded)} solved challenges')

  while True:
    logger.debug(f'Sleeping for {interval} seconds')
    time.sleep(interval)
    logger.info('Checking for first bloods')
    for challenge in get_challenges():
      if challenge['id'] in blooded:
        logger.debug(f'Skipping {challenge["name"]} ({challenge["id"]})')
        continue
      logger.debug(f'Checking {challenge["name"]} ({challenge["id"]})')
      if (blooder := get_blooder(challenge)) is not None:
        if notify(challenge, blooder).status_code in {200, 204}:
          blooded.add(challenge['id'])
        else:
          logger.error(f'Failed to notify {challenge["name"]} ({challenge["id"]})')

if __name__ == '__main__': main()
