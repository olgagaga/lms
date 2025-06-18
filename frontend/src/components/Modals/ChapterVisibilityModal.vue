<template>
	<Dialog
		v-model="show"
		:options="{
			title: 'Manage Chapter Visibility',
			size: 'md',
		}"
	>
		<template #body-content>
			<!-- Debug info -->
			<div class="text-xs text-gray-500 mb-4">
				<div>Loading: {{ chapters.loading }}</div>
				<div>Has Error: {{ !!chapters.error }}</div>
				<div>Has Data: {{ !!chapters.data }}</div>
				<div>Data Length: {{ chaptersData?.length }}</div>
				<div>First Chapter: {{ chaptersData?.[0]?.title }}</div>
				<div>Course: {{ course }}</div>
				<div>Batch: {{ batch }}</div>
				<div>typeof chaptersData: {{ typeof chaptersData }}</div>
				<div>typeof chaptersData.value: {{ typeof chaptersData?.value }}</div>
				<div>isProxy: {{ chaptersData && chaptersData.constructor && chaptersData.constructor.name === 'Proxy' }}</div>
				<div>chaptersData (stringified): {{ JSON.stringify(chaptersData) }}</div>
				<div>chaptersData.value (stringified): {{ JSON.stringify(chaptersData?.value) }}</div>
			</div>

			<div class="space-y-4">
				<!-- Loading State -->
				<div v-if="chapters.loading" class="text-center py-4">
					<LoadingText />
				</div>

				<!-- Error State -->
				<div v-else-if="chapters.error" class="text-center py-4 text-red-500">
					{{ __('Error loading chapters') }}
					<div class="text-sm mt-2">{{ chapters.error }}</div>
				</div>

				<!-- No Data State -->
				<div
					v-else-if="!chaptersData || chaptersData.length === 0"
					class="text-center py-4 text-gray-500"
				>
					{{ __('No chapters found') }}
				</div>

				<!-- Data State -->
				<div v-else :key="chaptersData.length">
					<div class="text-sm text-gray-600 mb-4">
						{{ __('Toggle visibility for each chapter') }}
					</div>
					<div
						v-for="chapter in chaptersData"
						:key="chapter.name"
						class="flex items-center justify-between p-3 bg-surface-gray-1 rounded-md mb-2"
					>
						<div class="font-medium">{{ chapter.title }}</div>
						<Switch
							:modelValue="!chapter.hidden_from_students"
							@update:modelValue="val => onSwitchUpdate(val, chapter)"
						/>
					</div>
				</div>
			</div>
		</template>
	</Dialog>
</template>

<script setup>
import { ref, watch, onMounted, onUpdated, onUnmounted, computed, nextTick } from 'vue'
import { Switch, LoadingText, Dialog } from 'frappe-ui'
import { createResource } from 'frappe-ui'

const props = defineProps({
	modelValue: {
		type: Boolean,
		required: true,
	},
	course: {
		type: String,
		required: true,
	},
	batch: {
		type: String,
		required: true,
	},
})

const emit = defineEmits(['update:modelValue', 'close'])

// Local show state for v-model
const show = ref(props.modelValue)

// Keep show in sync with modelValue prop
watch(
	() => props.modelValue,
	(val) => {
		show.value = val
	}
)
// Emit update when show changes
watch(show, (val) => {
	emit('update:modelValue', val)
})

// Debug logs for props
console.log('ChapterVisibilityModal props:', {
	course: props.course,
	batch: props.batch,
	isOpen: props.modelValue,
})

// Create a reactive computed property for chapters data
const chaptersData = computed(() => {
	// Normalize hidden_from_students to boolean
	return Array.isArray(chapters.data)
		? chapters.data.map(chapter => ({
			...chapter,
			hidden_from_students: Boolean(chapter.hidden_from_students),
		}))
		: []
})

// Computed property to help debug the current state
const debugState = computed(() => ({
	loading: chapters.loading,
	error: chapters.error,
	hasData: !!chapters.data,
	dataLength: chaptersData.value?.length,
	firstChapter: chaptersData.value?.[0],
	allChapters: chaptersData.value,
	typeofChaptersData: typeof chaptersData.value,
	typeofChapters: typeof chapters.data,
	isProxy: chaptersData.value && chaptersData.value.constructor && chaptersData.value.constructor.name === 'Proxy',
}))

const chapters = createResource({
	url: 'lms.lms.api.get_course_chapters',
	params: {
		course: props.course,
		batch: props.batch,
	},
	auto: false, // Changed to false to control when it loads
	onSuccess(data) {
		console.log('Chapters loaded successfully:', data)
		console.log('Current debug state:', debugState.value)
		nextTick(() => {
			console.log('After nextTick - chaptersData:', chaptersData.value)
			const modal = document.querySelector('.frappe-ui-dialog')
			const chapterList = document.querySelectorAll('.bg-surface-gray-1')
			console.log('Modal DOM:', modal)
			console.log('Chapter list DOM:', chapterList)
			if (modal) {
				console.log('Modal computed style:', window.getComputedStyle(modal))
			}
			if (chapterList.length) {
				chapterList.forEach((el, i) => {
					console.log(`Chapter item #${i} style:`, window.getComputedStyle(el))
				})
			}
		})
		if (data && data.length > 0) {
			console.log('First chapter details:', {
				name: data[0].name,
				title: data[0].title,
				hidden: data[0].hidden_from_students,
			})
		} else {
			console.log('No chapters returned from API')
		}
	},
	onError(error) {
		console.error('Error loading chapters:', error)
		console.log('Current debug state:', debugState.value)
		if (error.messages) {
			console.error('Error messages:', error.messages)
		}
		if (error.exc) {
			console.error('Exception:', error.exc)
		}
	},
})

// Watch for modal open state
watch(
	() => show.value,
	(newValue) => {
		console.log('[watch] Modal visibility changed:', newValue)
		if (newValue && props.course && props.batch) {
			console.log('[watch] Loading chapters for:', {
				course: props.course,
				batch: props.batch,
			})
			chapters.update({
				params: {
					course: props.course,
					batch: props.batch,
				},
			})
			chapters.reload()
		}
	},
	{ immediate: true },
)

// Watch for changes in chapters data with more explicit logging
watch(
	() => chapters.data,
	(newData, oldData) => {
		console.log('[watch] Chapters data changed from:', oldData, 'to:', newData)
		console.log('[watch] ChaptersData computed value:', chaptersData.value)
	},
	{ deep: true, immediate: true },
)

// Watch for changes in chaptersData (computed)
watch(
	() => chaptersData.value,
	(newVal, oldVal) => {
		console.log('[watch] chaptersData.value changed from:', oldVal, 'to:', newVal)
	},
	{ deep: true, immediate: true },
)

onMounted(() => {
	console.log('[lifecycle] ChapterVisibilityModal mounted')
	console.log('[lifecycle] Initial debug state:', debugState.value)
})

onUpdated(() => {
	console.log('[lifecycle] ChapterVisibilityModal updated')
	console.log('[lifecycle] Updated debug state:', debugState.value)
})

onUnmounted(() => {
	console.log('[lifecycle] ChapterVisibilityModal unmounted')
})

const updateChapterVisibility = (chapter, isVisible) => {
	console.log('[event] Updating chapter visibility:', {
		chapter: chapter.name,
		hidden: !isVisible,
		currentState: chapter.hidden_from_students,
		newState: !isVisible,
	})

	createResource({
		url: 'lms.lms.api.update_chapter_visibility',
		params: {
			course: props.course,
			batch: props.batch,
			visibility: JSON.stringify({ [chapter.name]: isVisible }),
		},
		onSuccess(data) {
			console.log('[event] Visibility updated successfully:', data)
			chapter.hidden_from_students = !isVisible
			chapters.reload()
		},
		onError(error) {
			console.error('[event] Error updating visibility:', error)
		},
	}).submit()
}

function onSwitchUpdate(val, chapter) {
	console.log('[event] Switch update:modelValue:', val, 'for chapter:', chapter)
	updateChapterVisibility(chapter, val)
}
</script>

<style scoped>
.bg-surface-gray-1 {
	background-color: var(--surface-gray-1);
}
</style>
