<template>
  <div class="quiz-navigation mt-4">
    <div class="flex flex-wrap gap-2 justify-center">
      <button
        v-for="index in totalQuestions"
        :key="index"
        @click="$emit('navigate', index)"
        class="w-8 h-8 flex items-center justify-center rounded border"
        :class="{
          'bg-white text-ink-gray-9 border-gray-300': !getQuestionStatus(index),
          'bg-blue-500 text-white border-blue-500': index === currentQuestion,
          'bg-green-300 text-black border-green-300': showAnswers && questionStatuses[index-1]?.isCorrect === true,
          'bg-red-300 text-black border-red-300': showAnswers && questionStatuses[index-1]?.isCorrect === false,
          'bg-gray-900 text-white border-gray-900': !showAnswers && questionStatuses[index-1]?.answered,
          'cursor-not-allowed': showAnswers && questionStatuses[index-1]?.answered,
          'cursor-pointer': !showAnswers || !questionStatuses[index-1]?.answered
        }"
        :disabled="showAnswers && questionStatuses[index-1]?.answered"
      >
        {{ index }}
      </button>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  totalQuestions: {
    type: Number,
    required: true
  },
  currentQuestion: {
    type: Number,
    required: true
  },
  questionStatuses: {
    type: Array,
    required: true
  },
  showAnswers: {
    type: Boolean,
    required: true
  }
})

const getQuestionStatus = (index) => {
  return props.questionStatuses[index - 1]
}

defineEmits(['navigate'])
</script> 