const BASE_URL = "http://localhost:5000/";


/**given keyword, generate html */
function generateKeywordHTML(keyword){
    return `<li data-id=${keyword.id}> ${keyword.word}  </li>`
}

/**put existing keyword on page */
async function showInitialKeyword(){
    const response = await axios.get(`${BASE_URL}`)
    const keyword_list = response.data.keywords
    return keyword_list
}


async function add_to_keyword_list(evt){
    evt.preventDefault();
    console.log(evt);
    
    let word = $(".kw").val()

    let keyword = await axios.post(`${BASE_URL}`,{word})

    let new_keyword = $(generateKeywordHTML(keyword.data.keyword))
    $("#keyword_list").append(new_keyword)


}

$("#add_keyword").on("submit", add_to_keyword_list)