from dummy_api_plugin import DummyApiPlugin


def main():
    username = input("Enter your username: ")
    password = input("Enter your password: ")

    plugin = DummyApiPlugin(username, password)
    # plugin.run()
    if plugin.connectivity_test():
        collected_data = plugin.collect()
        if collected_data:
            # for debuting purposes
            plugin.output(collected_data)
        else:
            print("No data collected.")


if __name__ == '__main__':
    main()
