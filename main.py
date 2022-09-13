from website import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True) #automatically reruns server every time smth is changed
    