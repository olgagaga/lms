<template>
	<div v-if="quiz.data">
		<div
			class="bg-surface-blue-2 space-y-1 py-2 px-2 mb-4 rounded-md text-sm text-ink-blue-3"
		>
			<div class="leading-5">
				{{
					__('This quiz consists of {0} questions.').format(questions.length)
				}}
			</div>
			<div v-if="quiz.data?.duration" class="leading-5">
				{{
					__(
						'Please ensure that you complete all the questions in {0} minutes.',
					).format(quiz.data.duration)
				}}
			</div>
			<div v-if="quiz.data?.duration" class="leading-5">
				{{
					__(
						'If you fail to do so, the quiz will be automatically submitted when the timer ends.',
					)
				}}
			</div>
			<div v-if="quiz.data.passing_percentage" class="leading-relaxed">
				{{
					__(
						'You will have to get {0}% correct answers in order to pass the quiz.',
					).format(quiz.data.passing_percentage)
				}}
			</div>
			<div v-if="quiz.data.max_attempts" class="leading-5">
				{{
					__('You can attempt this quiz {0}.').format(
						quiz.data.max_attempts == 1
							? '1 time'
							: `${quiz.data.max_attempts} times`,
					)
				}}
			</div>
		</div>

		<div v-if="quiz.data.duration" class="flex flex-col space-x-1 my-4">
			<div class="mb-2">
				<span class=""> {{ __('Time') }}: </span>
				<span class="font-semibold">
					{{ formatTimer(timer) }}
				</span>
			</div>
			<ProgressBar :progress="timerProgress" />
		</div>

		<div v-if="activeQuestion == 0">
			<div class="border text-center p-20 rounded-md">
				<div class="font-semibold text-lg text-ink-gray-9">
					{{ quiz.data.title }}
				</div>
				<Button
					v-if="
						!quiz.data.max_attempts ||
						attempts.data?.length < quiz.data.max_attempts
					"
					@click="startQuiz"
					class="mt-2"
				>
					<span>
						{{ __('Start') }}
					</span>
				</Button>
				<div v-else class="leading-5 text-ink-gray-7">
					{{
						__(
							'You have already exceeded the maximum number of attempts allowed for this quiz.',
						)
					}}
				</div>
			</div>
		</div>
		<div v-else-if="!quizSubmission.data">
			<div v-for="(question, qtidx) in questions">
				<div
					v-if="qtidx == activeQuestion - 1 && questionDetails.data"
					class="border rounded-md p-5"
				>
					<div class="flex justify-between">
						<div class="text-sm text-ink-gray-5">
							<span class="mr-2">
								{{ __('Question {0}').format(activeQuestion) }}:
							</span>
							<span>
								{{ getInstructions(questionDetails.data) }}
							</span>
						</div>
						<div
							class="text-ink-gray-9 text-sm font-semibold item-left flex items-center gap-2"
						>
							{{ question.marks }}
							{{ question.marks == 1 ? __('Mark') : __('Marks') }}
							<Checkbox
								size="sm"
								v-model="flaggedQuestions[activeQuestion - 1]"
								:label="__('Flag')"
							/>
						</div>
					</div>
					<div
						class="text-ink-gray-9 font-semibold mt-2 leading-5"
						v-html="questionDetails.data.question"
					></div>
					<div v-if="questionDetails.data.type == 'Choices'" v-for="index in 4">
						<label
							v-if="questionDetails.data[`option_${index}`]"
							:class="[
								'flex items-center rounded-md p-3 mt-4 w-full cursor-pointer focus:border-blue-600',
								selectedOptions[index - 1] ? 'bg-surface-gray-4' : 'bg-surface-gray-3'
							]"
						>
							<input
								v-if="!showAnswers.length && !questionDetails.data.multiple"
								type="radio"
								:name="encodeURIComponent(questionDetails.data.question)"
								class="w-3.5 h-3.5 text-ink-gray-9 focus:ring-outline-gray-modals"
								v-model="selectedOptions[index - 1]"
								:value="1"
								@change="markAnswer(index)"
							/>

							<input
								v-else-if="!showAnswers.length && questionDetails.data.multiple"
								type="checkbox"
								:name="encodeURIComponent(questionDetails.data.question)"
								class="w-3.5 h-3.5 text-ink-gray-9 rounded-sm focus:ring-outline-gray-modals"
								v-model="selectedOptions[index - 1]"
								:true-value="1"
								:false-value="0"
								@change="markAnswer(index)"
							/>
							<div
								v-else-if="quiz.data.show_answers"
								v-for="(answer, idx) in showAnswers"
							>
								<div v-if="index - 1 == idx">
									<CheckCircle
										v-if="answer == 1"
										class="w-4 h-4 text-ink-green-2"
									/>
									<MinusCircle
										v-else-if="answer == 2"
										class="w-4 h-4 text-ink-green-2"
									/>
									<XCircle
										v-else-if="answer == 0"
										class="w-4 h-4 text-ink-red-3"
									/>
									<MinusCircle v-else class="w-4 h-4" />
								</div>
							</div>
							<span
								class="ml-2"
								v-html="questionDetails.data[`option_${index}`]"
							>
							</span>
						</label>
						<div
							v-if="questionDetails.data[`explanation_${index}`]"
							class="mt-2 text-xs"
							v-show="showAnswers.length"
						>
							{{ questionDetails.data[`explanation_${index}`] }}
						</div>
					</div>
					<div v-else-if="questionDetails.data.type == 'User Input'">
						<FormControl
							v-model="possibleAnswer"
							type="textarea"
							:disabled="showAnswers.length ? true : false"
							class="my-2"
						/>
						<div v-if="showAnswers.length">
							<Badge v-if="showAnswers[0]" :label="__('Correct')" theme="green">
								<template #prefix>
									<CheckCircle class="w-4 h-4 text-ink-green-2 mr-1" />
								</template>
							</Badge>
							<Badge v-else theme="red" :label="__('Incorrect')">
								<template #prefix>
									<XCircle class="w-4 h-4 text-ink-red-3 mr-1" />
								</template>
							</Badge>
						</div>
					</div>
					<div v-else-if="questionDetails.data.type == 'Fill In'">
						<div class="space-y-4">
							<div class="text-ink-gray-9 font-medium mb-4">
								<span
									v-for="(part, index) in parsedFillInQuestion"
									:key="index"
								>
									<span v-if="part.type === 'text'">{{ part.value }}</span>
									<input
										v-else
										type="text"
										v-model="fillInAnswers[part.index]"
										:disabled="showAnswers.length ? true : false"
										:class="[
											'inline-block w-32 px-2 py-1 mx-1 border rounded-md focus:outline-none',
											showAnswers.length
												? showAnswers[part.index] === true
													? 'border-green-500 bg-green-50 text-green-900'
													: showAnswers[part.index] === false
														? 'border-red-500 bg-red-50 text-red-900'
														: ''
												: 'focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
										]"
										:placeholder="__('Answer')"
									/>
								</span>
							</div>
						</div>
					</div>
					<div v-else>
						<TextEditor
							class="mt-4"
							:content="possibleAnswer"
							@change="(val) => (possibleAnswer = val)"
							:editable="true"
							:fixedMenu="true"
							editorClass="prose-sm max-w-none border-b border-x bg-surface-gray-2 rounded-b-md py-1 px-2 min-h-[7rem]"
						/>
					</div>
					<div class="flex items-center justify-between mt-4">
						<div class="text-sm text-ink-gray-5">
							{{
								__('Question {0} of {1}').format(
									activeQuestion,
									questions.length,
								)
							}}
						</div>
						<Button
							v-if="
								quiz.data.show_answers &&
								!showAnswers.length &&
								questionDetails.data.type != 'Open Ended'
							"
							@click="checkAnswer()"
						>
							<span>
								{{ __('Check') }}
							</span>
						</Button>
						<Button v-else-if="!allQuestionsAnswered" @click="nextQuestion()">
							<span>
								{{ __('Next') }}
							</span>
						</Button>
						<Button v-else @click="submitQuiz()">
							<span>
								{{ __('Submit') }}
							</span>
						</Button>
					</div>

					<QuizNavigation
						:total-questions="questions.length"
						:current-question="activeQuestion"
						:question-statuses="questionStatuses"
						:show-answers="quiz.data?.show_answers"
						:flagged-questions="flaggedQuestions"
						:review-mode="quizSubmission.data && !quizSubmission.data.is_open_ended"
						@navigate="navigateToQuestion"
					/>
				</div>
			</div>
		</div>
		<div v-else>
			<div v-if="quizSubmission.data.is_open_ended" class="border rounded-md p-20 text-center space-y-2">
				<div class="text-lg font-semibold text-ink-gray-9">
					{{ __('Quiz Summary') }}
				</div>
				<div class="leading-5 text-ink-gray-7">
					{{ __('Your submission has been successfully saved. The instructor will review and grade it shortly, and you\'ll be notified of your final result.') }}
				</div>
			</div>
			<div v-else>
				<div v-for="(question, qtidx) in questions">
					<div v-if="qtidx == activeQuestion - 1 && questionDetailsStore[question.question]" class="border rounded-md p-5">
						<div class="flex justify-between">
							<div class="text-sm text-ink-gray-5">
								<span class="mr-2">
									{{ __('Question {0}').format(activeQuestion) }}:
								</span>
								<span>
									{{ getInstructions(questionDetailsStore[question.question]) }}
								</span>
							</div>
							<div class="text-ink-gray-9 text-sm font-semibold item-left flex items-center gap-2">
								{{ question.marks }}
								{{ question.marks == 1 ? __('Mark') : __('Marks') }}
							</div>
						</div>
						<div class="text-ink-gray-9 font-semibold mt-2 leading-5" v-html="questionDetailsStore[question.question].question"></div>
						<div v-if="questionDetailsStore[question.question].type == 'Choices'" v-for="index in 4">
							<label v-if="questionDetailsStore[question.question][`option_${index}`]"
								class="flex items-center bg-surface-gray-3 rounded-md p-3 mt-4 w-full">
								<input
									type="checkbox"
									:checked="userAnsweredOption(question, index)"
									disabled
									class="w-3.5 h-3.5 text-ink-gray-9 rounded-sm mr-2"
								/>
								<span class="ml-2" v-html="questionDetailsStore[question.question][`option_${index}`]"></span>
								<span v-if="userAnsweredOption(question, index)" class="ml-2">
									<CheckCircle v-if="isOptionCorrect(question, index)" class="w-4 h-4 text-ink-green-2" />
									<XCircle v-else class="w-4 h-4 text-ink-red-3" />
								</span>
							</label>
						</div>
						<div v-else-if="questionDetailsStore[question.question].type == 'User Input'">
							<FormControl
								:model-value="getUserAnswer(question)"
								type="textarea"
								disabled
								class="my-2"
							/>
							<Badge v-if="isUserInputCorrect(question)" :label="__('Correct')" theme="green">
								<template #prefix>
									<CheckCircle class="w-4 h-4 text-ink-green-2 mr-1" />
								</template>
							</Badge>
							<Badge v-else theme="red" :label="__('Incorrect')">
								<template #prefix>
									<XCircle class="w-4 h-4 text-ink-red-3 mr-1" />
								</template>
							</Badge>
						</div>
						<div v-else-if="questionDetailsStore[question.question].type == 'Fill In'">
							<div class="space-y-4">
								<div class="text-ink-gray-9 font-medium mb-4">
									<span v-for="(part, index) in parseFillInQuestion(questionDetailsStore[question.question].text_with_blanks)" :key="index">
										<span v-if="part.type === 'text'">{{ part.value }}</span>
										<input v-else type="text" :value="getFillInUserAnswer(question, part.index)" disabled
											:class="['inline-block w-32 px-2 py-1 mx-1 border rounded-md', isFillInCorrect(question, part.index) ? 'border-green-500 bg-green-50 text-green-900' : 'border-red-500 bg-red-50 text-red-900']"
										placeholder="Answer" />
									</span>
								</div>
							</div>
						</div>
						<div class="mt-2 text-xs text-ink-gray-7">
							<strong>{{ __('Correct Answer:') }}</strong>
							<span>{{ formatCorrectAnswer(questionDetailsStore[question.question]) }}</span>
						</div>
					</div>
				</div>
				<QuizNavigation
					:total-questions="questions.length"
					:current-question="activeQuestion"
					:question-statuses="reviewStatuses"
					:show-answers="true"
					:flagged-questions="flaggedQuestions"
					:review-mode="quizSubmission.data && !quizSubmission.data.is_open_ended"
					@navigate="navigateToQuestion"
					class="flex justify-center"
				/>
				<div class="mt-5 flex flex-col items-center justify-center">
    {{ __('You got {0}% correct answers with a score of {1} out of {2}').format(Math.ceil(quizSubmission.data.percentage), quizSubmission.data.score, quizSubmission.data.score_out_of) }}
    <div v-if="quizSubmission.data.percentage >= quiz.data.passing_percentage" class="text-green-700 font-semibold mt-2">
        {{ __("Congratulations! You passed the quiz and now can move on! Don't forget to analyze your mistakes") }}
    </div>
    <div v-else class="text-red-700 font-semibold mt-2">
        {{ __("Quiz Failed! You need to try one more time to get quiz passed! Good luck") }}
    </div>
    <Button @click="resetQuiz()" class="mt-5"
        v-if="!quiz.data.max_attempts || attempts?.data.length < quiz.data.max_attempts">
        <span>{{ __('Try Again') }}</span>
    </Button>
</div>
			</div>
		</div>
		<div
			v-if="
				quiz.data.show_submission_history &&
				attempts?.data &&
				attempts.data.length > 0
			"
			class="mt-10"
		>
			<ListView
				:columns="getSubmissionColumns()"
				:rows="attempts?.data"
				row-key="name"
				:options="{
					selectable: false,
					showTooltip: false,
					emptyState: { title: __('No Quiz submissions found') },
				}"
			>
			</ListView>
		</div>
	</div>
</template>
<script setup>
import {
	Badge,
	Button,
	call,
	createResource,
	ListView,
	TextEditor,
	FormControl,
	toast,
	Checkbox,
} from 'frappe-ui'
import { ref, watch, reactive, inject, computed } from 'vue'
import { CheckCircle, XCircle, MinusCircle } from 'lucide-vue-next'
import { timeAgo } from '@/utils'
import { useRouter } from 'vue-router'
import ProgressBar from '@/components/ProgressBar.vue'
import QuizNavigation from '@/components/QuizNavigation.vue'

const user = inject('$user')
const activeQuestion = ref(0)
const currentQuestion = ref('')
const selectedOptions = reactive([0, 0, 0, 0])
const showAnswers = reactive([])
let questions = reactive([])
const possibleAnswer = ref(null)
const timer = ref(0)
let timerInterval = null
const router = useRouter()
const fillInAnswers = ref([])
const parsedFillInQuestion = ref([])

// Add question statuses tracking
const questionStatuses = reactive([])

// Add a reactive array to track flagged questions
const flaggedQuestions = reactive([])

const allQuestionDetailsLoaded = ref(false)

const props = defineProps({
	quizName: {
		type: String,
		required: true,
	},
})

const quiz = createResource({
	url: 'frappe.client.get',
	makeParams(values) {
		return {
			doctype: 'LMS Quiz',
			name: props.quizName,
		}
	},
	cache: ['quiz', props.quizName],
	auto: true,
	transform(data) {
		data.duration = parseInt(data.duration)
	},
	onSuccess(data) {
		populateQuestions()
		setupTimer()
	},
})

// Initialize question statuses when questions are populated
const initializeQuestionStatuses = () => {
	questionStatuses.splice(0, questionStatuses.length)
	flaggedQuestions.splice(0, flaggedQuestions.length)
	questions.forEach(() => {
		questionStatuses.push({
			answered: false,
			isCorrect: null,
		})
		flaggedQuestions.push(false)
	})
}

// Update the populateQuestions function
const populateQuestions = () => {
	let data = quiz.data
	if (data.shuffle_questions) {
		questions = shuffleArray(data.questions)
		if (data.limit_questions_to) {
			questions = questions.slice(0, data.limit_questions_to)
		}
	} else {
		questions = data.questions
	}
	initializeQuestionStatuses()
}

const setupTimer = () => {
	if (quiz.data.duration) {
		timer.value = quiz.data.duration * 60
	}
}

const startTimer = () => {
	timerInterval = setInterval(() => {
		timer.value--
		if (timer.value == 0) {
			clearInterval(timerInterval)
			submitQuiz()
		}
	}, 1000)
}

const formatTimer = (seconds) => {
	const hrs = Math.floor(seconds / 3600)
		.toString()
		.padStart(2, '0')
	const mins = Math.floor((seconds % 3600) / 60)
		.toString()
		.padStart(2, '0')
	const secs = (seconds % 60).toString().padStart(2, '0')
	return hrs != '00' ? `${hrs}:${mins}:${secs}` : `${mins}:${secs}`
}

const timerProgress = computed(() => {
	return (timer.value / (quiz.data.duration * 60)) * 100
})

const shuffleArray = (array) => {
	for (let i = array.length - 1; i > 0; i--) {
		const j = Math.floor(Math.random() * (i + 1))
		;[array[i], array[j]] = [array[j], array[i]]
	}
	return array
}

const attempts = createResource({
	url: 'frappe.client.get_list',
	makeParams(values) {
		return {
			doctype: 'LMS Quiz Submission',
			filters: {
				member: user.data?.name,
				quiz: quiz.data?.name,
			},
			fields: [
				'name',
				'creation',
				'score',
				'score_out_of',
				'percentage',
				'passing_percentage',
			],
			order_by: 'creation desc',
		}
	},
	transform(data) {
		data.forEach((submission, index) => {
			submission.creation = timeAgo(submission.creation)
			submission.idx = index + 1
		})
	},
})

watch(
	() => quiz.data,
	() => {
		if (quiz.data) {
			populateQuestions()
		}
		if (quiz.data && quiz.data.max_attempts) {
			attempts.reload()
			resetQuiz()
		}
	},
)

const quizSubmission = createResource({
	url: 'lms.lms.doctype.lms_quiz.lms_quiz.quiz_summary',
	makeParams(values) {
		return {
			quiz: quiz.data.name,
			results: localStorage.getItem(quiz.data.title),
		}
	},
})

const questionDetails = createResource({
	url: 'lms.lms.utils.get_question_details',
	makeParams(values) {
		return {
			question: currentQuestion.value,
		}
	},
})

watch(activeQuestion, (value) => {
	if (value > 0) {
		currentQuestion.value = quiz.data.questions[value - 1].question
		questionDetails.reload()
	}
})

watch(
	questionDetails,
	(newValue) => {
		if (newValue?.data?.type === 'Fill In') {
			try {
				if (!newValue.data.text_with_blanks) {
					console.error('Text with blanks is not defined')
					toast.error(__('Error: Text with blanks is missing'))
					return
				}
				const blankCount =
					newValue.data.text_with_blanks.match(/\\__(\d+)__/g)?.length || 0
				fillInAnswers.value = new Array(blankCount).fill('')
				parsedFillInQuestion.value = parseFillInQuestion(
					newValue.data.text_with_blanks,
				)
			} catch (error) {
				console.error('Error parsing fill-in question:', error)
				toast.error(__('Error loading question. Please try again.'))
			}
		}
	},
	{ deep: true },
)

watch(
	() => props.quizName,
	(newName) => {
		if (newName) {
			quiz.reload()
		}
	},
)

const startQuiz = () => {
	activeQuestion.value = 1
	localStorage.removeItem(quiz.data.title)
	if (quiz.data.duration) startTimer()
}

const markAnswer = (index) => {
	if (!questionDetails.data.multiple)
		selectedOptions.splice(0, selectedOptions.length, ...[0, 0, 0, 0])
	selectedOptions[index - 1] = selectedOptions[index - 1] ? 0 : 1
}

const stripHtml = (html) => {
	const tmp = document.createElement('DIV')
	tmp.innerHTML = html
	return tmp.textContent || tmp.innerText || ''
}

const parseFillInQuestion = (question) => {
	const parts = []
	let regex = /\\__(\d+)__/g
	let lastIndex = 0
	let match
	const cleanQuestion = stripHtml(question)

	while ((match = regex.exec(cleanQuestion)) !== null) {
		if (match.index > lastIndex) {
			parts.push({
				type: 'text',
				value: cleanQuestion.slice(lastIndex, match.index),
			})
		}
		parts.push({ type: 'blank', index: parseInt(match[1]) - 1 })
		lastIndex = regex.lastIndex
	}
	if (lastIndex < cleanQuestion.length) {
		parts.push({ type: 'text', value: cleanQuestion.slice(lastIndex) })
	}
	return parts
}

const getAnswers = () => {
	if (questionDetails.data.type === 'Choices') {
		return selectedOptions
			.map((option, index) =>
				option ? questionDetails.data[`option_${index + 1}`] : null,
			)
			.filter(Boolean)
	} else if (questionDetails.data.type === 'Fill In') {
		const requiredBlanks =
			questionDetails.data.text_with_blanks.match(/__(\d+)__/g)?.length || 0
		const answers = fillInAnswers.value.slice(0, requiredBlanks)
		const allFilled = answers.every((answer) => answer && answer.trim() !== '')
		if (!allFilled) {
			return []
		}
		return answers
	} else {
		return [possibleAnswer.value]
	}
}

const checkAnswer = (questionContext = null, isSubmit = false) => {
	const context = questionContext || {
		questionName: currentQuestion.value,
		questionDetails: questionDetails.data,
		answers: getAnswers(),
		selectedOptions: [...selectedOptions],
		questionIndex: activeQuestion.value - 1,
	}

	let answers = context.answers
	const showWarning = allQuestionsAnswered.value || quiz.data.show_answers

	if (context.questionDetails.type === 'Choices' && !answers.length) {
		if (!isSubmit && showWarning) toast.warning(__('Please select an option'))
		return
	}
	if (context.questionDetails.type === 'Fill In') {
		const requiredBlanks = context.questionDetails.text_with_blanks.match(/__(\d+)__/g)?.length || 0
		const allFilled = answers.length === requiredBlanks && answers.every((a) => a && a.trim() !== '')
		if (!allFilled) {
			if (!isSubmit && showWarning) toast.warning(__('Please fill in all blanks'))
			return
		}
	}
	if (context.questionDetails.type === 'User Input' && !answers[0]) {
		if (!isSubmit && showWarning) toast.warning(__('Please enter an answer'))
		return
	}

	createResource({
		url: 'lms.lms.doctype.lms_quiz.lms_quiz.check_answer',
		params: {
			question: context.questionName,
			type: context.questionDetails.type,
			answers: JSON.stringify(answers),
		},
		auto: true,
		onSuccess(data) {
			let tempShowAnswers = []
			let type = context.questionDetails.type
			if (type == 'Choices') {
				context.selectedOptions.forEach((option, index) => {
					if (option) {
						tempShowAnswers[index] = option && data[index]
					} else if (data[index] == 2) {
						tempShowAnswers[index] = 2
					} else {
						tempShowAnswers[index] = undefined
					}
				})
				const isCorrect = data.every(
					(val, idx) => !context.selectedOptions[idx] || val === 1,
				)
				questionStatuses[context.questionIndex] = {
					answered: true,
					isCorrect: isCorrect,
				}
			} else if (type == 'Fill In') {
				tempShowAnswers = [...data]
				const isCorrect = data.every((val) => val === true)
				questionStatuses[context.questionIndex] = {
					answered: true,
					isCorrect: isCorrect,
				}
			} else if (type == 'User Input') {
				tempShowAnswers = [data]
				const isCorrect = data === true
				questionStatuses[context.questionIndex] = {
					answered: true,
					isCorrect: isCorrect,
				}
			}

			addToLocalStorage(context.questionName, context.answers, tempShowAnswers)
			if (quiz.data.show_answers) {
				showAnswers.splice(0, showAnswers.length, ...tempShowAnswers)
			}
		},
	})
}

const addToLocalStorage = (
	questionName,
	answers,
	correctness = [undefined],
) => {
	let quizData = JSON.parse(localStorage.getItem(quiz.data.title)) || []
	quizData = quizData.filter(entry => entry.question_name !== questionName)
	// If correctness is empty, set to [false] for User Input
	if ((!correctness || correctness.length === 0 || correctness.every(x => x === undefined)) && questionDetails.data?.type === 'User Input') {
		correctness = [false]
	}
	let questionData = {
		question_name: questionName,
		answer: answers.join(),
		is_correct: correctness.filter((answer) => {
			return answer != undefined
		}),
	}
	quizData.push(questionData)
	localStorage.setItem(quiz.data.title, JSON.stringify(quizData))
}

// Add a computed property to check if all questions are answered
const allQuestionsAnswered = computed(() => {
	return questionStatuses.every((status) => status.answered)
})

// Update nextQuestion function to find next unanswered question
const nextQuestion = () => {
	const currentQuestionIndex = activeQuestion.value - 1
	const currentQuestionType = questionDetails.data?.type

	if (!quiz.data.show_answers && currentQuestionType != 'Open Ended') {
		const context = {
			questionName: currentQuestion.value,
			questionDetails: questionDetails.data,
			answers: getAnswers(),
			selectedOptions: [...selectedOptions],
			questionIndex: currentQuestionIndex,
		}
		if (context.answers.length > 0) {
			checkAnswer(context)
		}
	} else if (currentQuestionType == 'Open Ended') {
		const answers = getAnswers()
		if (answers[0]) {
			addToLocalStorage(currentQuestion.value, answers)
			questionStatuses[currentQuestionIndex].answered = true
		}
	}

	// Find the next unanswered question
	let nextUnansweredIndex = questionStatuses.findIndex((status, index) => {
		return index > currentQuestionIndex && !status.answered
	})

	// If no unanswered questions after current, look from beginning
	if (nextUnansweredIndex === -1) {
		nextUnansweredIndex = questionStatuses.findIndex(
			(status) => !status.answered,
		)
	}

	// If all questions are answered or no more unanswered questions, stay on current question
	if (nextUnansweredIndex === -1) {
		return
	}

	activeQuestion.value = nextUnansweredIndex + 1
}

const resetQuestion = () => {
	if (activeQuestion.value == quiz.data.questions.length) return
	activeQuestion.value = activeQuestion.value + 1
}

const submitQuiz = () => {
	if (!quiz.data.show_answers) {
		// Always save the last question's answer before submitting, for all types
		const context = {
			questionName: currentQuestion.value,
			questionDetails: questionDetails.data,
			answers: getAnswers(),
			selectedOptions: [...selectedOptions],
			questionIndex: activeQuestion.value - 1,
		}
		const type = context.questionDetails.type
		if (
			(type === 'Fill In' && context.answers.length === (context.questionDetails.text_with_blanks.match(/__(\d+)__/g)?.length || 0) && context.answers.every((a) => a && a.trim() !== '')) ||
			(type === 'Choices' && context.answers.length > 0) ||
			(type === 'User Input' && context.answers[0]) ||
			(type === 'Open Ended' && context.answers[0])
		) {
			checkAnswer(context, true)
		}
		setTimeout(() => {
			createSubmission()
		}, 500)
		return
	}
	createSubmission()
}

const resetQuiz = () => {
	activeQuestion.value = 0
	selectedOptions.splice(0, selectedOptions.length, ...[0, 0, 0, 0])
	showAnswers.length = 0
	quizSubmission.reset()
	populateQuestions()
	setupTimer()
}

const getInstructions = (question) => {
	if (question.type == 'Choices')
		if (question.multiple) return __('Choose all answers that apply')
		else return __('Choose one answer')
	else return __('Type your answer')
}

const markLessonProgress = () => {
	if (router.currentRoute.value.name == 'Lesson') {
		call('lms.lms.api.mark_lesson_progress', {
			course: router.currentRoute.value.params.courseName,
			chapter_number: router.currentRoute.value.params.chapterNumber,
			lesson_number: router.currentRoute.value.params.lessonNumber,
		})
	}
}

const getSubmissionColumns = () => {
	return [
		{
			label: 'No.',
			key: 'idx',
		},
		{
			label: 'Date',
			key: 'creation',
		},
		{
			label: 'Score',
			key: 'score',
			align: 'center',
		},
		{
			label: 'Score out of',
			key: 'score_out_of',
			align: 'center',
		},
		{
			label: 'Percentage',
			key: 'percentage',
			align: 'center',
		},
	]
}

// Update navigateToQuestion function
const navigateToQuestion = (index) => {
	// Always allow navigation in review mode (after submission, not open-ended)
	if (quizSubmission.data && !quizSubmission.data.is_open_ended) {
		activeQuestion.value = index
		return
	}

	if (quiz.data.show_answers && questionStatuses[index - 1]?.answered) {
		// Don't allow navigation to answered questions when show_answers is enabled
		return
	}

	if (quiz.data.show_answers || questionDetails.data?.type == 'Open Ended') {
		activeQuestion.value = index
	} else {
		// Save current answer before navigating
		if (questionDetails.data?.type == 'Open Ended') {
			const answers = getAnswers()
			addToLocalStorage(currentQuestion.value, answers)
			questionStatuses[activeQuestion.value - 1] = {
				answered: true,
				isCorrect: null,
			}
		} else if (
			questionDetails.data?.type == 'User Input' &&
			possibleAnswer.value
		) {
			const answers = getAnswers()
			questionStatuses[activeQuestion.value - 1] = {
				answered: true,
				isCorrect: null,
			}
			addToLocalStorage(currentQuestion.value, answers)
		} else {
			checkAnswer()
		}
		// Navigate after a short delay to ensure answer is saved
		setTimeout(() => {
			activeQuestion.value = index
		}, 500)
	}
}

// Add this to your script setup section

// Store for question details
const questionDetailsStore = reactive({})

// Function to load all question details
const loadAllQuestionDetails = async () => {
	allQuestionDetailsLoaded.value = false
	for (const q of questions) {
		try {
			const details = await call('lms.lms.utils.get_question_details', {
				question: q.question,
			})
			questionDetailsStore[q.question] = details
		} catch (error) {
			console.error(`Error loading details for question ${q.question}:`, error)
		}
	}
	allQuestionDetailsLoaded.value = true
}

// Helper functions
const formatUserAnswer = (answer, questionType, questionDetails) => {
	if (!answer) return '-'

	switch (questionType) {
		case 'Choices':
			// If answer contains option IDs, convert to option text
			if (questionDetails && answer) {
				const answerArray = answer.split(',')
				const optionTexts = answerArray
					.map((optionText) => {
						// Find which option number this text corresponds to
						for (let i = 1; i <= 4; i++) {
							if (questionDetails[`option_${i}`] === optionText.trim()) {
								return questionDetails[`option_${i}`]
							}
						}
						return optionText.trim()
					})
					.filter(Boolean)
				return optionTexts.join(', ')
			}
			return answer
		case 'Fill In':
			return answer.split(',').join(', ')
		case 'User Input':
			return answer
		case 'Open Ended':
			const text = stripHtml(answer)
			return text.length > 100 ? text.substring(0, 100) + '...' : text
		default:
			return answer
	}
}

const formatCorrectAnswer = (questionDetails) => {
	if (!questionDetails) {
		console.log('no question details retrieved')
		return '-'
	}

	console.log(questionDetails)

	switch (questionDetails.type) {
		case 'Choices':
			const correctOptions = []
			for (let i = 1; i <= 4; i++) {
				if (questionDetails[`is_correct_${i}`]) {
					correctOptions.push(stripHtml(questionDetails[`option_${i}`]))
				}
			}
			return correctOptions.length > 0 ? correctOptions.join(', ') : '-'

		case 'Fill In':
			if (questionDetails.correct_answers) {
				return Array.isArray(questionDetails.correct_answers)
					? questionDetails.correct_answers.join('; ')
					: questionDetails.correct_answers
			}
			return '-'

		case 'User Input':
			const correctOptionsInput = []
			for (let i = 1; i <= 4; i++) {
				if (questionDetails[`possibility_${i}`]) {
					correctOptionsInput.push(
						stripHtml(questionDetails[`possibility_${i}`]),
					)
				}
			}
			return correctOptionsInput.length > 0
				? correctOptionsInput.join('; ')
				: '-'

		case 'Open Ended':
			return __('Subjective')

		default:
			return questionDetails.correct_answer || '-'
	}
}

const calculateMarksReceived = (userEntry, question) => {
	if (!userEntry.is_correct) return 0

	if (Array.isArray(userEntry.is_correct)) {
		// Count correct answers
		const correctCount = userEntry.is_correct.filter(
			(answer) => answer === 1 || answer === true,
		).length
		const totalAnswers = userEntry.is_correct.length

		// For partial credit
		if (correctCount === totalAnswers) {
			return question.marks // Full marks
		} else if (correctCount > 0) {
			return Math.round((correctCount / totalAnswers) * question.marks) // Partial marks
		}
		return 0
	} else {
		// Single answer question
		return userEntry.is_correct === 1 || userEntry.is_correct === true
			? question.marks
			: 0
	}
}

// Updated summaryRows computed property
const summaryRows = computed(() => {
	if (!quiz.data || !quizSubmission.data) return []
	// This line ensures reactivity
	const detailsKeys = Object.keys(questionDetailsStore)
	let quizData = JSON.parse(localStorage.getItem(quiz.data.title) || '[]')
	return questions.map((q, idx) => {
		const userEntry =
			quizData.find((entry) => entry.question_name === q.question) || {}
		const questionDetails = questionDetailsStore[q.question]
		return {
			id: idx + 1,
			question: questionDetails
				? stripHtml(questionDetails.question)
				: `Question ${idx + 1}`,
			yourAnswer: formatUserAnswer(
				userEntry.answer,
				questionDetails?.type,
				questionDetails,
			),
			correctAnswer: formatCorrectAnswer(questionDetails),
			marksReceived: `${calculateMarksReceived(userEntry, q)}/${q.marks}`,
		}
	})
})

// Update the createSubmission function to load question details
const createSubmission = () => {
	quizSubmission.submit(
		{},
		{
			async onSuccess(data) {
				// Load all question details for the summary
				await loadAllQuestionDetails()

				markLessonProgress()
				if (quiz.data && quiz.data.max_attempts) attempts.reload()
				if (quiz.data.duration) clearInterval(timerInterval)
			},
			onError(err) {
				const errorTitle = err?.message || ''
				if (errorTitle.includes('MaximumAttemptsExceededError')) {
					const errorMessage = err.messages?.[0] || err
					toast.error(__(errorMessage))
					setTimeout(() => {
						window.location.reload()
					}, 3000)
				}
			},
		},
	)
}

// --- Add review mode helpers ---
// Get user's answer for a question (from localStorage/quizSubmission)
const getUserEntry = (question) => {
	let quizData = JSON.parse(localStorage.getItem(quiz.data.title) || '[]')
	return quizData.find((entry) => entry.question_name === question.question) || {}
}
const getUserAnswer = (question) => getUserEntry(question).answer || ''
const userAnsweredOption = (question, index) => {
	const entry = getUserEntry(question)
	if (!entry.answer) return false
	return entry.answer.split(',').map(a => a.trim()).includes(questionDetailsStore[question.question][`option_${index}`])
}
const isOptionCorrect = (question, index) => {
	const entry = getUserEntry(question)
	if (!entry.answer) return false
	const correctOptions = []
	for (let i = 1; i <= 4; i++) {
		if (questionDetailsStore[question.question][`is_correct_${i}`]) {
			correctOptions.push(questionDetailsStore[question.question][`option_${i}`])
		}
	}
	return correctOptions.includes(questionDetailsStore[question.question][`option_${index}`])
}
const isUserInputCorrect = (question) => {
	const entry = getUserEntry(question)
	if (!entry.answer) return false
	const correctPossibilities = []
	for (let i = 1; i <= 4; i++) {
		if (questionDetailsStore[question.question][`possibility_${i}`]) {
			correctPossibilities.push(questionDetailsStore[question.question][`possibility_${i}`])
		}
	}
	return correctPossibilities.includes(entry.answer)
}
const getFillInUserAnswer = (question, idx) => {
	const entry = getUserEntry(question)
	if (!entry.answer) return ''
	const answers = entry.answer.split(',')
	return answers[idx] || ''
}
const isFillInCorrect = (question, idx) => {
	const entry = getUserEntry(question)
	if (!entry.is_correct) return false
	return Array.isArray(entry.is_correct) ? (entry.is_correct[idx] === 1 || entry.is_correct[idx] === true) : (entry.is_correct === 1 || entry.is_correct === true)
}
// For navigation, always show green/red for correct/incorrect
const reviewStatuses = computed(() => {
	return questions.map((q) => {
		const entry = getUserEntry(q)
		if (!entry.is_correct) return { answered: !!entry.answer, isCorrect: false }
		if (Array.isArray(entry.is_correct)) {
			const allCorrect = entry.is_correct.every((v) => v === 1 || v === true)
			return { answered: !!entry.answer, isCorrect: allCorrect }
		} else {
			return { answered: !!entry.answer, isCorrect: entry.is_correct === 1 || entry.is_correct === true }
		}
	})
})

watch(
	() => quizSubmission.data,
	(newVal) => {
		if (newVal && !newVal.is_open_ended) {
			loadAllQuestionDetails()
		}
	}
)

// Restore user's previous answer for the current question
const restoreUserAnswer = () => {
	const entry = getUserEntry({ question: currentQuestion.value })
	const qType = questionDetails.data?.type

	if (!entry || !qType) return

	if (qType === 'Choices') {
		selectedOptions.splice(0, selectedOptions.length, ...[0, 0, 0, 0])
		if (entry.answer) {
			const answers = entry.answer.split(',').map(a => stripHtml(a.trim()))
			for (let i = 0; i < 4; i++) {
				const opt = stripHtml(questionDetails.data[`option_${i + 1}`] || '')
				selectedOptions[i] = answers.includes(opt) ? 1 : 0
			}
		}
	} else if (qType === 'User Input') {
		possibleAnswer.value = entry.answer || ''
	} else if (qType === 'Fill In') {
		if (entry.answer) {
			const answers = entry.answer.split(',')
			fillInAnswers.value = answers
		}
	} else {
		possibleAnswer.value = entry.answer || ''
	}
}

// Watch for questionDetails.data to be loaded, then restore answer
watch(
	() => questionDetails.data,
	(val) => {
		if (val && !quiz.data.show_answers) {
			restoreUserAnswer()
		}
	}
)
</script>
<style>
p {
	line-height: 1.5rem;
}
</style>
