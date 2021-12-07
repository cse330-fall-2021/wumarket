const favoriteButtons = document.getElementsByClassName("favorite-button")
for (let i=0; i<favoriteButtons.length; i++) {
	favoriteButtons[i].addEventListener('click', () => {
		console.log('clicked:' + favoriteButtons[i].parentNode.parentNode.id)
		toFavorite(favoriteButtons[i].parentNode.parentNode.id)
})
}
function toFavorite(id) {
	window.location.pathname = "/add_favorite" + "/" + id
}




// let sendMessageButtons = document.getElementsByClassName("message-button");
// for (let i=0; i < sendMessageButtons.length; i++) {
// 	curButton = sendMessageButtons[i];
// 	curButton.addEventListener("click", function() {
// 		let curItem = curButton;
// 		while( !curItem.classList.contains("item") )
// 			curItem = curItem.parentElement
// 		console.log("send message of item was clicked");
// 		console.log(curItem.id);
// 	})
// }

const editButtons = document.getElementsByClassName("edit-button");
for (let i=0; i<editButtons.length; i++) {
	editButtons[i].addEventListener('click', () => {
		console.log('clicked:' + editButtons[i].parentNode.parentNode.id)
		toEdit(editButtons[i].parentNode.parentNode.id)
})
}
function toEdit(id) {
	window.location.pathname = "/edit_product" + "/" + id
}
