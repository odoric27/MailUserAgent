from clients import mail_client
import argparse

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('-default', action='store_true')
	args = parser.parse_args()

	client = mail_client.MailClient(default=args.default)
	client.run()
	print("\nLoading...\n")