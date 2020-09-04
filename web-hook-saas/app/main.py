from flask import Flask, request, jsonify

app = Flask(__name__)

hook_map = {}

@app.route("/")
def hello():
    return "Hello World from Flask"


@app.route('/post_web_hook', methods=['POST'])
def post_web_hook():
    """
    Receive a POST request with information on the 
    webhook the service should send 
    (headers, request type, POST body, URL params, etc) apple
    """
    data = request.form.to_dict(flat=False)
    
    # generate id
    hook_id = generate_hook_id()
    
    # save to dict key id -> web_hook data,
    hook_map[hook_id] = {'web_hook_info': data}
    
    # return id
    return jsonify({'hook_id': hook_id})


def generate_hook_id():
    return 0

if __name__ == "__main__":
    # Only for debugging while developing
    app.run(host='0.0.0.0', debug=True, port=80)