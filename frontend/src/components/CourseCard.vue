<template>
	<div class="flex flex-col">
		<router-link
			:to="{
				name: 'CourseDetail',
				params: {
					courseName: course.name,
				},
			}"
			class="block"
		>
			<div
				v-if="course.title"
				class="flex flex-col h-full rounded-md border-2 overflow-auto"
				style="min-height: 350px"
			>
				<div
					class="course-image"
					:class="{ 'default-image': !course.image }"
					:style="{ backgroundImage: 'url(\'' + encodeURI(course.image) + '\')' }"
				>
					<div class="flex items-center flex-wrap relative top-4 px-2 w-fit">
						<Badge
							v-if="course.featured"
							variant="subtle"
							theme="green"
							size="md"
							class="mb-1 mr-1"
						>
							{{ __('Featured') }}
						</Badge>
						<div
							v-if="course.tags"
							v-for="tag in course.tags?.split(', ')"
							class="text-xs bg-white text-gray-800 px-2 py-0.5 rounded-md mb-1 mr-1"
						>
							{{ tag }}
						</div>
					</div>
					<div v-if="!course.image" class="image-placeholder">
						{{ course.title[0] }}
					</div>
				</div>
				<div class="flex flex-col flex-auto p-4">
					<div class="flex items-center justify-between mb-2">
						<div v-if="course.lessons">
							<Tooltip :text="__('Lessons')">
								<span class="flex items-center text-ink-gray-7">
									<BookOpen class="h-4 w-4 stroke-1.5 mr-1" />
									{{ course.lessons }}
								</span>
							</Tooltip>
						</div>

						<div v-if="course.enrollments">
							<Tooltip :text="__('Enrolled Students')">
								<span class="flex items-center text-ink-gray-7">
									<Users class="h-4 w-4 stroke-1. mr-1" />
									{{ course.enrollments }}
								</span>
							</Tooltip>
						</div>

						<div v-if="course.rating">
							<Tooltip :text="__('Average Rating')">
								<span class="flex items-center text-ink-gray-7">
									<Star class="h-4 w-4 stroke-1.5 mr-1" />
									{{ course.rating }}
								</span>
							</Tooltip>
						</div>

						<div v-if="course.status != 'Approved'">
							<Badge
								variant="subtle"
								:theme="course.status === 'Under Review' ? 'orange' : 'blue'"
								size="sm"
							>
								{{ course.status }}
							</Badge>
						</div>
					</div>

					<div class="text-xl font-semibold leading-6 text-ink-gray-9">
						{{ course.title }}
					</div>

					<div class="short-introduction text-ink-gray-7 text-sm">
						{{ course.short_introduction }}
					</div>

					<ProgressBar
						v-if="user && course.membership"
						:progress="course.membership.progress"
					/>

					<div
						v-if="user && course.membership"
						class="text-sm text-ink-gray-7 mt-2 mb-4"
					>
						{{ Math.ceil(course.membership.progress) }}% completed
					</div>

					<div class="flex items-center justify-between mt-auto">
						<div class="flex avatar-group overlap">
							<div
								class="h-6 mr-1"
								:class="{ 'avatar-group overlap': course.instructors.length > 1 }"
							>
								<UserAvatar
									v-for="instructor in course.instructors"
									:user="instructor"
								/>
							</div>
							<CourseInstructors :instructors="course.instructors" />
						</div>

						<div class="flex items-center space-x-2">
							<div v-if="course.paid_course" class="font-semibold">
								{{ course.price }}
							</div>
							<div
								v-if="course.paid_certificate || course.enable_certification"
								class="text-xs text-ink-blue-3 bg-surface-blue-1 py-0.5 px-1 rounded-md"
							>
								{{ __('Certification') }}
							</div>
						</div>
					</div>
				</div>
			</div>
		</router-link>
		<Button
			v-if="isBatchView && user?.data?.is_moderator"
			variant="subtle"
			size="sm"
			class="w-full mt-2"
			@click="openChapterVisibilityModal"
		>
			<template #prefix>
				<Eye class="h-4 w-4" />
			</template>
			{{ __('Manage Visibility') }}
		</Button>
	</div>
	<ChapterVisibilityModal
		v-if="showChapterVisibilityModal"
		v-model="showChapterVisibilityModal"
		:course="course.name"
		:batch="course.batch"
		@close="showChapterVisibilityModal = false"
	/>
</template>
<script setup>
import { BookOpen, Users, Star, Eye } from 'lucide-vue-next'
import UserAvatar from '@/components/UserAvatar.vue'
import { sessionStore } from '@/stores/session'
import { Badge, Tooltip, Button } from 'frappe-ui'
import CourseInstructors from '@/components/CourseInstructors.vue'
import ProgressBar from '@/components/ProgressBar.vue'
import ChapterVisibilityModal from '@/components/Modals/ChapterVisibilityModal.vue'
import { ref, inject, watch } from 'vue'

const user = inject('$user')
const showChapterVisibilityModal = ref(false)

const props = defineProps({
	course: {
		type: Object,
		required: true,
	},
	isBatchView: {
		type: Boolean,
		default: false
	}
})

const openChapterVisibilityModal = () => {
	console.log('Opening chapter visibility modal with course:', {
		name: props.course.name,
		batch: props.course.batch,
		isBatchView: props.isBatchView
	})
	showChapterVisibilityModal.value = true
}

// Add a watch to monitor course changes
watch(() => props.course, (newCourse) => {
	console.log('Course data changed:', newCourse)
}, { deep: true })
</script>
<style>
.course-image {
	height: 168px;
	width: 100%;
	background-size: cover;
	background-position: center;
	background-repeat: no-repeat;
}

.course-card-pills {
	background: #ffffff;
	margin-left: 0;
	margin-right: 0.5rem;
	padding: 3.5px 8px;
	font-size: 11px;
	text-align: center;
	letter-spacing: 0.011em;
	text-transform: uppercase;
	font-weight: 600;
	width: fit-content;
}

.default-image {
	display: flex;
	flex-direction: column;
	align-items: center;
	background-color: theme('colors.green.100');
	color: theme('colors.green.600');
}

.avatar-group {
	display: inline-flex;
	align-items: center;
}

.avatar-group .avatar {
	transition: margin 0.1s ease-in-out;
}
.image-placeholder {
	display: flex;
	align-items: center;
	flex: 1;
	font-size: 5rem;
	color: theme('colors.gray.700');
	font-weight: 600;
}
.avatar-group.overlap .avatar + .avatar {
	margin-left: calc(-8px);
}

.short-introduction {
	display: -webkit-box;
	-webkit-line-clamp: 2;
	-webkit-box-orient: vertical;
	text-overflow: ellipsis;
	width: 100%;
	overflow: hidden;
	margin: 0.25rem 0 1.25rem;
	line-height: 1.5;
}
</style>
