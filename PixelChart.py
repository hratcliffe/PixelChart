import GUI
from sys import argv

if __name__ == "__main__":

  try:
    GUI.run_app(argv)
  except Exception as e:
    # Swallow everything while developing...
    print(e)
