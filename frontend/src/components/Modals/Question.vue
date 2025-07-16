<template>
	<Dialog
		v-model="show"
		:options="{
			size: '3xl',
		}"
	>
		<template #body>
			<div class="p-5 space-y-5">
				<div class="text-lg font-semibold text-ink-gray-9 mb-5">
					{{ __(props.title) }}
				</div>
				<div
					v-if="!editMode"
					class="flex items-center text-xs text-ink-gray-7 space-x-5"
				>
					<Switch
						size="sm"
						:label="__('Choose an existing question')"
						v-model="chooseFromExisting"
						class="!p-0"
					/>
				</div>
				<div v-if="!chooseFromExisting || editMode" class="space-y-2">
					<div>
						<label class="block text-xs text-ink-gray-5 mb-1">
							{{ __('Question') }}
						</label>
						<TextEditor
							:content="question.question"
							@change="(val) => (question.question = val)"
							:editable="true"
							:fixedMenu="true"
							editorClass="prose-sm max-w-none border-b border-x bg-surface-gray-2 rounded-b-md py-1 px-2 min-h-[7rem]"
						/>
					</div>
					<div class="grid grid-cols-2 gap-4">
						<FormControl
							v-model="question.subject"
							:label="__('Subject')"
							type="text"
						/>
						<FormControl
							v-model="question.skill"
							:label="__('Skill')"
							type="text"
						/>
					</div>
					<div class="grid grid-cols-2 gap-4">
						<FormControl
							v-model="question.complexity_initial"
							:label="__('Complexity Initial (0-1)')"
							type="number"
							:min="0"
							:max="1"
							:step="0.01"
						/>
						<FormControl
							v-model="question.complexity_adapted"
							:label="__('Complexity Adapted (0-1)')"
							type="number"
							:min="0"
							:max="1"
							:step="0.01"
						/>
					</div>
					<div class="grid grid-cols-2 gap-4">
						<FormControl
							v-model="question.marks"
							:label="__('Marks')"
							type="number"
						/>
						<FormControl
							:label="__('Type')"
							v-model="question.type"
							type="select"
							:options="['Choices', 'User Input', 'Open Ended', 'Fill In']"
							class="pb-2"
							:required="true"
						/>
					</div>
					<div
						v-if="question.type == 'Choices'"
						class="text-base font-semibold text-ink-gray-9 mb-5 mt-5"
					>
						{{ __('Options') }}
					</div>
					<div
						v-else-if="question.type == 'User Input'"
						class="text-base font-semibold text-ink-gray-9 mb-5 mt-5"
					>
						{{ __('Possibilities') }}
					</div>
					<div
						v-else-if="question.type == 'Fill In'"
						class="text-base font-semibold text-ink-gray-9 mb-5 mt-5"
					>
						{{ __('Fill In Answers') }}
					</div>
					<div v-if="question.type == 'Choices'" class="grid grid-cols-2 gap-4">
						<div v-for="n in 4" class="space-y-4 py-2">
							<FormControl
								:label="__('Option') + ' ' + n"
								v-model="question[`option_${n}`]"
								:required="n <= 2 ? true : false"
							/>
							<FormControl
								:label="__('Explanation')"
								v-model="question[`explanation_${n}`]"
							/>
							<FormControl
								:label="__('Correct Answer')"
								v-model="question[`is_correct_${n}`]"
								type="checkbox"
							/>
						</div>
					</div>
					<div
						v-else-if="question.type == 'User Input'"
						class="grid grid-cols-2 gap-4 py-2"
					>
						<div v-for="n in 4">
							<FormControl
								:label="__('Possibility') + ' ' + n"
								v-model="question[`possibility_${n}`]"
								:required="n == 1 ? true : false"
							/>
						</div>
					</div>
					<div
						v-else-if="question.type == 'Fill In'"
						class="space-y-4 py-2"
					>
						<div class="text-sm text-ink-gray-5 mb-2">
							{{ __('Use \\__1__, \\__2__, etc. in your question text to mark blanks.') }}
						</div>
						<div class="mb-4">
							<label class="block text-xs text-ink-gray-5 mb-1">
								{{ __('Text with Blanks') }}
							</label>
							<TextEditor
								:content="question.text_with_blanks"
								@change="(val) => (question.text_with_blanks = val)"
								:editable="true"
								:fixedMenu="true"
								editorClass="prose-sm max-w-none border-b border-x bg-surface-gray-2 rounded-b-md py-1 px-2 min-h-[7rem]"
							/>
						</div>
						<div v-for="n in 4" class="grid grid-cols-2 gap-4">
							<FormControl
								:label="__('Correct Answer') + ' ' + n"
								v-model="question[`correct_answer_${n}`]"
								type="text"
								:required="n == 1 ? true : false"
							/>
							<FormControl
								:label="__('Case Sensitive')"
								v-model="question[`case_sensitive_${n}`]"
								type="checkbox"
							/>
						</div>
					</div>
				</div>
				<div v-else-if="chooseFromExisting" class="space-y-4">
					<pre class="bg-surface-gray-2 p-2 text-xs rounded mb-2">
						subjectOptions: {{ subjectOptions }}
						skillOptions: {{ skillOptions }}
						filteredQuestions: {{ filteredQuestions }}
						filterSubjects: {{ filterSubjects }}
						filterSkills: {{ filterSkills }}
						filterComplexity: {{ filterComplexity }}
						filterTypes: {{ filterTypes }}
					</pre>
					<!-- Advanced Filter UI -->
					<div class="grid grid-cols-2 gap-4 mb-4">
						<MultiSelect
							v-model="filterSubjects"
							:label="__('Subject')"
							:options="subjectOptions"
							@update:modelValue="onSubjectChange"
						/>
						<MultiSelect
							v-model="filterSkills"
							:label="__('Skill')"
							:options="skillOptions"
						/>
					</div>
					<div class="grid grid-cols-2 gap-4 mb-4">
						<MultiSelect
							v-model="filterComplexity"
							:label="__('Complexity')"
							:options="complexityOptions"
						/>
						<MultiSelect
							v-model="filterTypes"
							:label="__('Question Type')"
							:options="typeOptions"
						/>
					</div>
					<!-- Filtered Questions List -->
					<div class="mb-4">
						<label class="block text-xs text-ink-gray-5 mb-2">{{ __('Select question(s)') }}</label>
						<div class="max-h-48 overflow-y-auto border rounded p-3 bg-surface-gray-1">
							<div v-if="filteredQuestions.length === 0" class="text-sm text-ink-gray-5">
								{{ __('No questions match the selected filters.') }}
							</div>
							<div v-else v-for="q in filteredQuestions" :key="q.name" class="flex items-center mb-2 p-2 hover:bg-surface-gray-2 rounded">
								<input
									type="checkbox"
									:value="q.name"
									v-model="existingQuestion.selected"
									class="mr-3 h-4 w-4"
								/>
								<div class="flex-1">
									<span class="font-medium text-sm">{{ q.question }}</span>
									<div class="text-xs text-ink-gray-5">
										{{ q.subject }} / {{ q.skill }} / {{ q.type }} / {{ q.complexity_initial }}
									</div>
								</div>
							</div>
						</div>
					</div>
					<FormControl
						v-model="existingQuestion.marks"
						:label="__('Marks')"
						type="number"
					/>
				</div>
				<div class="flex items-center justify-end space-x-2 mt-5">
					<Button variant="solid" @click="submitQuestion()">
						{{ __('Submit') }}
					</Button>
				</div>
			</div>
		</template>
	</Dialog>
</template>
<script setup>
import {
	Dialog,
	FormControl,
	TextEditor,
	 createResource,
	Switch,
	Button,
	toast,
	call
} from 'frappe-ui'
import { computed, watch, reactive, ref, inject, onMounted, toRaw } from 'vue'
import Link from '@/components/Controls/Link.vue'
import { useOnboarding } from 'frappe-ui/frappe'
import MultiSelect from '@/components/Controls/MultiSelect.vue'

const show = defineModel()
const quiz = defineModel('quiz')
const chooseFromExisting = ref(false)
const editMode = ref(false)
const user = inject('$user')
const { updateOnboardingStep } = useOnboarding('learning')

const filterSubjects = ref([])
const filterSkills = ref([])
const filterComplexity = ref([])
const filterTypes = ref([])
const subjectOptions = ref([])
const skillOptions = ref([])
const complexityOptions = [
	{ value: '0-0.25', description: '[0;0.25)' },
	{ value: '0.25-0.5', description: '[0.25;0.5)' },
	{ value: '0.5-0.75', description: '[0.5;0.75)' },
	{ value: '0.75-1', description: '[0.75;1]' },
]
const typeOptions = [
	{ value: 'Choices', description: 'Choices' },
	{ value: 'User Input', description: 'User Input' },
	{ value: 'Open Ended', description: 'Open Ended' },
	{ value: 'Fill In', description: 'Fill In' },
]
const filteredQuestions = ref([])

// Debug: Watchers for all relevant refs
watch(subjectOptions, (val) => {
	console.log('[DEBUG] subjectOptions changed:', val)
})
watch(skillOptions, (val) => {
	console.log('[DEBUG] skillOptions changed:', val)
})
watch(filteredQuestions, (val) => {
	console.log('[DEBUG] filteredQuestions changed:', val)
})
watch(filterSubjects, (val) => {
	console.log('[DEBUG] filterSubjects changed:', val)
})
watch(filterSkills, (val) => {
	console.log('[DEBUG] filterSkills changed:', val)
})
watch(filterComplexity, (val) => {
	console.log('[DEBUG] filterComplexity changed:', val)
})
watch(filterTypes, (val) => {
	console.log('[DEBUG] filterTypes changed:', val)
})

const existingQuestion = reactive({
	selected: [],
	marks: 1,
})
const question = reactive({
	question: '',
	subject: '',
	skill: '',
	complexity_initial: 0,
	complexity_adapted: 0,
	type: 'Choices',
	marks: 1,
})

const populateFields = () => {
	let fields = ['option', 'is_correct', 'explanation', 'possibility', 'blank', 'correct_answer']
	let counter = 1
	fields.forEach((field) => {
		while (counter <= 4) {
			question[`${field}_${counter}`] = field === 'is_correct' ? false : null
			counter++
		}
	})
}

populateFields()

const props = defineProps({
	title: {
		type: String,
		default: __('Add a new question'),
	},
	questionDetail: {
		type: [Object, null],
		required: true,
	},
})

const questionData = createResource({
	url: 'frappe.client.get',
	makeParams() {
		return {
			doctype: 'LMS Question',
			name: props.questionDetail.question,
		}
	},
	auto: false,
	onSuccess(data) {
		let counter = 1
		editMode.value = true
		Object.keys(data).forEach((key) => {
			if (Object.hasOwn(question, key)) question[key] = data[key]
		})
		while (counter <= 4) {
			question[`is_correct_${counter}`] = data[`is_correct_${counter}`]
				? true
				: false
			counter++
		}
		question.marks = props.questionDetail.marks
	},
})

watch(show, () => {
	if (show.value) {
		console.log('[Modal] Opened: show.value = true');
		editMode.value = false
		if (props.questionDetail.question) {
			console.log('[Modal] Editing existing question:', props.questionDetail.question);
			questionData.fetch()
		} else {
			console.log('[Modal] Adding new question');
			question.question = ''
			question.marks = 1
			question.type = 'Choices'
			existingQuestion.selected = []
			existingQuestion.marks = 1
			chooseFromExisting.value = false
			populateFields()
		}

		if (props.questionDetail.marks) console.log('[Modal] Setting marks from props:', props.questionDetail.marks);
		if (props.questionDetail.marks) question.marks = props.questionDetail.marks

		console.log('[Modal] Fetching subjects, skills, questions...');
		fetchSubjects()
		fetchSkills()
		fetchQuestions()
	}
})

const questionRow = createResource({
	url: 'frappe.client.insert',
	makeParams(values) {
		return {
			doc: {
				doctype: 'LMS Quiz Question',
				parent: quiz.value.data.name,
				parentfield: 'questions',
				parenttype: 'LMS Quiz',
				...values,
			},
		}
	},
})

const questionCreation = createResource({
	url: 'frappe.client.insert',
	makeParams(values) {
		let doc = {
			doctype: 'LMS Question',
			...question,
		}

		if (question.type === 'Fill In') {
			doc.fill_in_answers = []
			for (let i = 1; i <= 4; i++) {
				if (question[`correct_answer_${i}`]) {
					doc.fill_in_answers.push({
						blank_number: i,
						correct_answer: question[`correct_answer_${i}`],
						case_sensitive: question[`case_sensitive_${i}`] || false
					})
				}
			}
		}

		return { doc }
	},
})

const submitQuestion = () => {
	if (props.questionDetail?.question) updateQuestion()
	else addQuestion()
}

const addQuestion = () => {
	if (chooseFromExisting.value) {
		addQuestionRow({
			question: existingQuestion.selected,
			marks: existingQuestion.marks,
		})
	} else {
		questionCreation.submit(
			{},
			{
				onSuccess(data) {
					addQuestionRow({
						question: data.name,
						marks: question.marks,
					})
				},
				onError(err) {
					toast.error(err.messages?.[0] || err)
				},
			}
		)
	}
}

const addQuestionRow = (question) => {
	questionRow.submit(
		{
			...question,
		},
		{
			onSuccess() {
				if (user.data?.is_system_manager)
					updateOnboardingStep('create_first_quiz')

				show.value = false
				toast.success(__('Question added successfully'))
				quiz.value.reload()
				show.value = false
			},
			onError(err) {
				toast.error(err.messages?.[0] || err)
				show.value = false
			},
		}
	)
}

const questionUpdate = createResource({
	url: 'frappe.client.set_value',
	auto: false,
	makeParams(values) {
		return {
			doctype: 'LMS Question',
			name: questionData.data?.name,
			fieldname: {
				...question,
			},
		}
	},
})

const marksUpdate = createResource({
	url: 'frappe.client.set_value',
	auto: false,
	makeParams(values) {
		return {
			doctype: 'LMS Quiz Question',
			name: props.questionDetail.name,
			fieldname: {
				marks: question.marks,
			},
		}
	},
})

const updateQuestion = () => {
	questionUpdate.submit(
		{},
		{
			onSuccess() {
				marksUpdate.submit(
					{},
					{
						onSuccess() {
							show.value = false
							toast.success(__('Question updated successfully'))
							quiz.value.reload()
						},
					}
				)
			},
			onError(err) {
				toast.error(err.messages?.[0] || err)
			},
		}
	)
}

// Fetch subjects and skills
const fetchSubjects = async () => {
	console.log('[fetchSubjects] Called');
	try {
		const res = await call('lms.lms.utils.get_question_subjects')
		console.log('[fetchSubjects] Response:', res);
		// Check what res actually contains
		subjectOptions.value = (res || []).map(s => ({ value: s, description: s }))
		console.log('[fetchSubjects] subjectOptions.value set to:', toRaw(subjectOptions.value))
	} catch (err) {
		console.error('[fetchSubjects] Error:', err);
	}
}
const fetchSkills = async () => {
	console.log('[fetchSkills] Called with subjects:', filterSubjects.value);
	try {
		const res = await call('lms.lms.utils.get_question_skills', { subject: JSON.stringify(filterSubjects.value) })
		console.log('[fetchSkills] Response:', res);
		skillOptions.value = (res || []).map(s => ({ value: s, description: s }))
		console.log('[fetchSkills] skillOptions.value set to:', toRaw(skillOptions.value))
	} catch (err) {
		console.error('[fetchSkills] Error:', err);
	}
}
const fetchQuestions = async () => {
	const params = {}
	if (filterSubjects.value.length) params.subject = JSON.stringify(filterSubjects.value)
	if (filterSkills.value.length) params.skill = JSON.stringify(filterSkills.value)
	if (filterComplexity.value.length) params.complexity = JSON.stringify(filterComplexity.value)
	if (filterTypes.value.length) params.type = JSON.stringify(filterTypes.value)
	console.log('[fetchQuestions] Called with params:', params);
	try {
		const res = await call('lms.lms.utils.get_questions_filtered', params)
		console.log('[fetchQuestions] Response:', res);
		filteredQuestions.value = res || []
		console.log('[fetchQuestions] filteredQuestions.value set to:', toRaw(filteredQuestions.value))
	} catch (err) {
		console.error('[fetchQuestions] Error:', err);
	}
}

const onSubjectChange = async () => {
	await fetchSkills()
	await fetchQuestions()
}
watch(
	[() => filterSubjects.value, () => filterSkills.value, () => filterComplexity.value, () => filterTypes.value], 
	fetchQuestions,
	{deep: true}
)

onMounted(() => {
	fetchSubjects()
	fetchSkills()
	fetchQuestions()
})
</script>
<style>
input[type='radio']:checked {
	background-color: theme('colors.gray.900') !important;
	border-color: theme('colors.gray.900') !important;
	--tw-ring-color: theme('colors.gray.900') !important;
}
</style>