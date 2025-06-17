<template>
	<Dialog
		:modelValue="modelValue"
		@update:modelValue="$emit('update:modelValue', $event)"
		:title="__('Manage Chapter Visibility')"
		:size="'md'"
	>
		<div class="space-y-4">
			<div v-if="chapters.loading" class="text-center py-4">
				<LoadingText />
			</div>
			<div v-else-if="chapters.error" class="text-center py-4 text-red-500">
				{{ __('Error loading chapters') }}
				<div class="text-sm mt-2">{{ chapters.error }}</div>
			</div>
			<div v-else class="space-y-4">
				<div v-if="!chapters.data?.length" class="text-center py-4 text-gray-500">
					{{ __('No chapters found') }}
				</div>
				<div v-for="chapter in chapters.data" :key="chapter.name" class="flex items-center justify-between p-3 bg-surface-gray-1 rounded-md">
					<div class="font-medium">{{ chapter.title }}</div>
					<Switch
						v-model="chapter.hidden_from_students"
						@update:modelValue="updateChapterVisibility(chapter)"
					/>
				</div>
			</div>
		</div>
	</Dialog>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { Switch, LoadingText, Dialog } from 'frappe-ui'
import { createResource } from 'frappe-ui'

const props = defineProps({
	modelValue: {
		type: Boolean,
		required: true
	},
	course: {
		type: String,
		required: true
	},
	batch: {
		type: String,
		required: true
	}
})

const emit = defineEmits(['update:modelValue', 'close'])

// Debug logs for props
console.log('ChapterVisibilityModal props:', {
	course: props.course,
	batch: props.batch,
	isOpen: props.modelValue
})

const chapters = createResource({
	url: 'lms.lms.api.get_course_chapters',
	params: {
		course: props.course,
		batch: props.batch
	},
	auto: true,
	onSuccess(data) {
		console.log('Chapters loaded successfully:', data)
	},
	onError(error) {
		console.error('Error loading chapters:', error)
	}
})

// Watch for modal open state
watch(() => props.modelValue, (newValue) => {
	console.log('Modal visibility changed:', newValue)
	if (newValue) {
		console.log('Reloading chapters...')
		chapters.reload()
	}
})

const updateChapterVisibility = (chapter) => {
	console.log('Updating chapter visibility:', {
		chapter: chapter.name,
		hidden: chapter.hidden_from_students
	})
	
	createResource({
		url: 'lms.lms.api.update_chapter_visibility',
		params: {
			course: props.course,
			batch: props.batch,
			visibility: JSON.stringify({ [chapter.name]: !chapter.hidden_from_students })
		},
		onSuccess(data) {
			console.log('Visibility updated successfully:', data)
		},
		onError(error) {
			console.error('Error updating visibility:', error)
		}
	}).submit()
}

onMounted(() => {
	console.log('ChapterVisibilityModal mounted')
})
</script> 