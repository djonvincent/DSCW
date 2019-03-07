import Pyro4

fe = Pyro4.Proxy('PYRONAME:FrontEnd')

while True:
    print('\nWhat do you want to do?\n(1) Retrieve a movie\n(2) Rate a movie\n')
    choice = input()
    if choice == '1':
        movie_id = input('Enter movie ID: ')
        try:
            result = fe.get_movie(movie_id)
            if 'error' in result:
                print('Error: ' + result['error'])
            else:
                movie = result['result']
                print('\nTitle: ' + movie['title'])
                print(f'Rating: {movie["avg"]} ({movie["num"]} reviews)')
        except KeyError:
            print('Movie not found')
    elif choice == '2':
        movie_id = input('Enter movie ID: ')
        while True:
            rating = input('Enter rating (0-5): ')
            try:
                rating = float(rating)
                if rating < 0 or rating > 5:
                    raise ValueError
                break
            except ValueError:
                print('Not a number between 0 and 5')
        try:
            result = fe.add_rating(movie_id, rating)
            if 'error' in result:
                print('Error: ' + result['error'])
            else:
                print('Rating submitted')
        except KeyError:
            print('Movie not found')
        except ValueError:
            print('Please rate between 0 and 5')
