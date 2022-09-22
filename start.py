from app import init_app

app = init_app()

if __name__ == '__main__':
    # Starts the main app.
    app.run(debug=app.config['DEBUG'])

