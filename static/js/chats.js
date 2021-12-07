var cur_id = null;
socket = io.connect('http://' + document.domain + ':' + location.port + '/chats');
socket.on('incomingMessage', function(data) {
	console.log("received incoming message from js")
	if (data.msg != "" && cur_id != data.sender_id)
		addMessageToDOM(data.msg, true, data.sender_id);
});

// add listener to message form
document.getElementById("message-input-form").addEventListener("submit", function(e) {
	e.preventDefault();
	let submittedForm = e.target;
	let messageField = submittedForm['message-input'];
	addMessageToDOM(messageField.value, false);
	let fd = new FormData();
	// {{ session['test'] = 'testing session' }}
	// console.log(session['chat_with_id']);
	fd.append('message', messageField.value);
	let api_link = 'http://' + document.domain + ':' + location.port + '/add_message';

	fetch(api_link, {
        method: 'POST',
        body: fd
    }).then(
        response => response.json()
    ).then(data => {
        console.log("finished")
    });

    // socketio
    socket.emit('broadcastMessage', {'msg': messageField.value});

    messageField.value = "";
});

function addMessageToDOM(mes, guest_message, other_id) {

	if (cur_id == null) {
		console.log("please select a chat head");
		return;
	}

	let messagesDetailEle = document.getElementById("messages-detail");

	let newMesEle = document.createElement("p");
	newMesEle.classList.add("message");
	if (guest_message)
		newMesEle.classList.add("other-mes");
	else
		newMesEle.classList.add("user-mes")
	newMesEle.innerText = mes;

	let newMesLineEle = document.createElement("div");
	newMesLineEle.classList.add("message-line");
	newMesLineEle.appendChild(newMesEle);
	messagesDetailEle.appendChild(newMesLineEle);
	scrollMessagesToBottom()

	// update last message

}
// 


// Add listener for chat heads
let chat_heads = document.getElementsByClassName("message-head")
for (let i=0; i < chat_heads.length; i++) {
	chat_heads[i].addEventListener("click", function(e) {

		// front end effect
		prev_selected = document.getElementsByClassName("selected")
		for(let j=0; j < prev_selected.length; j++) {
			prev_selected[j].classList.remove("selected");
		}
		selected = e.target;
		while (!selected.classList.contains("message-head")) {
			selected = selected.parentElement;
		}
		selected.classList.add("selected")


		// send selected to flask
		let fd = new FormData();
		fd.append('other_user_id', selected.id);
		let api_link = 'http://' + document.domain + ':' + location.port + '/change_chathead';
		console.log("fetching " + selected.id);
		fetch(api_link, {
	        method: 'POST',
	        body: fd
	    }).then(
	        response => response.json()
	    ).then(data => {
	        console.log("chat head switched");
	        console.log(data['messages']);
	        let messagesDetailEle = document.getElementById("messages-detail");
	        messagesDetailEle.innerHTML = "";
	        cur_id = data['cur_user_id'];
	        for(let i=0; i < data['messages'].length; i++) {
	        	mes = data['messages'][i];
	        	guest_message = mes['sender_id'] != data['cur_user_id'];
	        	addMessageToDOM(mes['message'], guest_message, selected.id);
	        }

			// join chatroom
			socket.emit('joined', {});
	    });
	    	

		})
}

function scrollMessagesToBottom() {
	let messagesDetailEle = document.getElementById("messages-detail");
	messagesDetailEle.scrollTop = messagesDetailEle.scrollHeight;
}



// var socket;
// document.getElementById('message-input-form').addEventListener("submit", function(e) {
// 	e.preventDefault();
// 	var values = $(this).seralize();
// 	alert(values);
// });

