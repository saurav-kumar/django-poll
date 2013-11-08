import datetime

from django.utils import timezone
from django.test import TestCase
from django.core.urlresolvers import reverse

from polls.models import Poll

# Create your tests here.

class PollMethodTests(TestCase):

    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() should return False for questions whose
        pub_date is in the future
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Poll(pub_date=time)
        self.assertEqual(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() should return False for questions whose
        pub_date is older than 1 day
        """
        time = timezone.now() - datetime.timedelta(days=30)
        old_question = Poll(pub_date=time)
        self.assertEqual(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() should return True for questions whose
        pub_date is within the last day
        """
        time = timezone.now() - datetime.timedelta(hours=1)
        recent_question = Poll(pub_date=time)
        self.assertEqual(recent_question.was_published_recently(), True)

def create_poll(question, days):
        """
        Creates a poll with the given `question` published the given
        number of `days` offset to now (negative for polls published
        in the past, positive for polls that have yet to be published).
        """

        time = timezone.now() + datetime.timedelta(days=days)
        return Poll.objects.create(question=question, pub_date=time)

class PollViewTests(TestCase):
    def test_index_view_with_no_polls(self):
        """
        If no questions exist, an appropriate message should be displayed.
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_poll_list'], [])
    
    def test_index_view_with_a_past_poll(self):
        """
        Questions with a pub_date in the past should be displayed on the
        index page
        """
        create_poll(question="Past Poll.", days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_poll_list'],
            ['<Poll: Past Poll.>']
        )

    def test_index_view_with_a_future_poll(self):
        """
        Questions with a pub_date in the future should not be displayed on
        the index page.
        """
        create_poll(question = "Future Poll.", days = 30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.",
                            status_code=200)
        self.assertQuerysetEqual(response.context['latest_poll_list'], [])

    def test_index_view_with_future_poll_and_past_poll(self):
        """
        Even if both past and future questions exist, only Past Polls
        should be displayed.
        """
        create_poll(question="Past Poll.", days=-30)
        create_poll(question="Future Poll.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_poll_list'],
            ['<Poll: Past Poll.>']
        )

    def test_index_view_with_two_past_polls(self):
        """
        The questions index page may display multiple questions.
        """
        create_poll(question = "Past Poll 1.", days = -30)
        create_poll(question = "Past Poll 2.", days = -5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_poll_list'],
            ['<Poll: Past Poll 2.>', '<Poll: Past Poll 1.>']
        )

class PollIndexDetailTests(TestCase):
    def test_detail_view_with_a_future_poll(self):
        """
        The detail view of a question with a pub_date in the future should
        return a 404 not found.
        """
        future_poll = create_poll(question = 'Future Poll.', days = 5)
        response = self.client.get(reverse('polls:detail',
                                           args = (future_poll.id,)))
        self.assertEqual(response.status_code, 404)

    def test_detail_view_with_a_past_poll(self):
        """
        The detail view of a question with a pub_date in the past should
        display the question's text.
        """
        past_poll = create_poll(question = "Past Poll.", days=-5)
        response = self.client.get(reverse('polls:detail', args=(past_poll.id,)))
        self. assertContains(response, past_poll.question, status_code=200)


        
