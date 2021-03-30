import GUI
from sys import argv

if __name__ == "__main__":

  try:
    GUI.run_app(argv)
  except:
    # Swallow everything while developing...
    pass
