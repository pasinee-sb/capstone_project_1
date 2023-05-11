let BASE_URL = "https://reddi-senti.onrender.com"; //use when it production env
// let BASE_URL = "http://localhost:5000"; //use when in development env
const currentYear = new Date().getFullYear();
const $yearElement = $("#currentYear");
$yearElement.text(currentYear);

async function populate_analyze_form(vals) {
  $("#checkboxes").empty();

  vals.forEach((val) => {
    let checkbox = $("<input>").attr({
      type: "checkbox",
      name: "keywords[]",
      value: val,
      id: val,
    });
    let label = $("<label>").attr({ for: val }).text(val);
    let delete_btn = $(
      `<a href="#" class="delete_keyword" data-value=${val}><i class="fa-solid fa-trash-can text-danger"></i></a>`
    );
    delete_btn.on("click", delete_keyword);
    $("#checkboxes").append(
      $("<p>").append(checkbox).append(label).append(delete_btn)
    );
  });
}

async function get_session() {
  const response = await axios.get(`${BASE_URL}/session`);

  const sessionData = response.data;

  populate_analyze_form(sessionData.keywords);

  // prints the list of keywords in the session
}

async function add_word(evt) {
  evt.preventDefault(); // prevent form submission
  console.log(evt.target);

  const keyword = $("#word").val();
  console.log(keyword);

  const json = { word: keyword };

  const response = await axios.post(
    `${BASE_URL}/add_keyword`,
    JSON.stringify(json),
    {
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
    }
  );
  let newWords = response.data.keywords;
  console.log(newWords);

  populate_analyze_form(newWords);
  $("#word").val("");
}

$("#add_keyword").on("submit", add_word);
$(".delete_keyword").on("click", delete_keyword);

async function delete_keyword(e) {
  e.preventDefault();
  console.log(this.parentElement);
  console.log($(this));
  let word = $(this).data("value");
  $(this).parent().remove();

  const response = await axios.post(`/remove_keyword/${word}`);

  console.log(response);
}

//show any keywords added to the list during session, if any
$(get_session);
