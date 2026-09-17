let selectedForm = "ALL";
let selectedTopic = "ALL";

const searchInput = document.getElementById("searchInput");
const resultCount = document.getElementById("resultCount");

searchInput.addEventListener("input", filterQuestions);


document.querySelectorAll("#formFilters button").forEach(button => {
    button.addEventListener("click", () => {
        document.querySelectorAll("#formFilters button")
            .forEach(btn => btn.classList.remove("active"));

        button.classList.add("active");
        selectedForm = button.dataset.form;
        filterQuestions();
    });
});


document.querySelectorAll("#topicFilters button").forEach(button => {
    button.addEventListener("click", () => {
        document.querySelectorAll("#topicFilters button")
            .forEach(btn => btn.classList.remove("active"));

        button.classList.add("active");
        selectedTopic = button.dataset.topic;
        filterQuestions();
    });
});


function filterQuestions() {
    const search = searchInput.value.toLowerCase().trim();
    const cards = document.querySelectorAll(".question-card");
    let count = 0;

    cards.forEach(card => {
        const question = card.querySelector(".question-text")
            .textContent.toLowerCase();

        const form = card.dataset.form;
        const topic = card.dataset.topic;

        const matchSearch = question.includes(search);
        const matchForm = selectedForm === "ALL" || form === selectedForm;
        const matchTopic = selectedTopic === "ALL" || topic === selectedTopic;

        if (matchSearch && matchForm && matchTopic) {
            card.style.display = "block";
            count++;
        } else {
            card.style.display = "none";
        }
    });

    resultCount.textContent = count;
}


function openModal(id) {
    document.getElementById(id).classList.remove("hidden");
}


function closeModal(id) {
    document.getElementById(id).classList.add("hidden");
}


function openAddModal() {
    openModal("addModal");
}


function openFormModal() {
    openModal("formModal");
}


function openTopicModal() {
    openModal("topicModal");
}


function openManageModal() {
    openModal("manageModal");
}


function openEditModal(id, question, formId, topicId) {
    document.getElementById("editQuestionInput").value = question;
    document.getElementById("editFormSelect").value = formId;
    document.getElementById("editTopicSelect").value = topicId;

    document.getElementById("editForm").action = `/edit/${id}`;

    openModal("editModal");
}


window.addEventListener("click", event => {
    if (event.target.classList.contains("modal")) {
        event.target.classList.add("hidden");
    }
});
