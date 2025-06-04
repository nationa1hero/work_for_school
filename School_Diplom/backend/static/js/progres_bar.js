// Получаем элемент контейнера прогресс-бара
const progressContainer = document.querySelector('.progress-container');

// Получаем значение процента из атрибута data-progress
const progressPercentage = parseFloat(progressContainer.getAttribute('data-progress'));
console.log(progressPercentage)

// Устанавливаем ширину прогресс-бара и отображаем процент
document.getElementById('progress-bar').style.width = progressPercentage + '%';
