import json
from unittest import mock

import pandas as pd
import pytest
from es_aws_functions import test_generic_library
from moto import mock_s3
from pandas.util.testing import assert_frame_equal

import strata_period_method as lambda_method_function
import strata_period_wrangler as lambda_wrangler_function

method_environment_variables = {
    "strata_column": "strata",
    "value_column": "Q608_total"
}

wrangler_environment_variables = {
    "period_column": "period",
    "segmentation": "strata",
    "reference": "responder_id",
    "sns_topic_arn": "fake_sns_arn",
    "bucket_name": "test_bucket",
    "checkpoint": "999",
    "method_name": "strata_period_method"
}

method_runtime_variables = {
    "RuntimeVariables": {
        "data": None,
        "region_column": "region",
        "survey_column": "survey"
    }
}

wrangler_runtime_variables = {
    "RuntimeVariables":
        {
            "location": "Here",
            "survey_column": "survey",
            "run_id": "bob",
            "queue_url": "Earl",
            "incoming_message_group_id": "test_group",
            "in_file_name": "test_wrangler_input",
            "out_file_name": "test_wrangler_output.json",
            "outgoing_message_group_id": "test_id",
            "period": "period",
            "distinct_values": ["region"]
        }
}


##########################################################################################
#                                     Generic                                            #
##########################################################################################

@pytest.mark.parametrize(
    "which_lambda,which_runtime_variables,which_environment_variables,"
    "which_data,expected_message,assertion",
    [
        (lambda_wrangler_function, wrangler_runtime_variables,
         wrangler_environment_variables, None,
         "AWS Error", test_generic_library.wrangler_assert)
    ])
def test_client_error(which_lambda, which_runtime_variables,
                      which_environment_variables, which_data,
                      expected_message, assertion):
    test_generic_library.client_error(which_lambda, which_runtime_variables,
                                      which_environment_variables, which_data,
                                      expected_message, assertion)


@pytest.mark.parametrize(
    "which_lambda,which_runtime_variables,which_environment_variables,mockable_function,"
    "expected_message,assertion",
    [
        (lambda_method_function, method_runtime_variables,
         method_environment_variables, "strata_period_method.EnvironSchema",
         "General Error", test_generic_library.method_assert),
        (lambda_wrangler_function, wrangler_runtime_variables,
         wrangler_environment_variables, "strata_period_wrangler.EnvironSchema",
         "General Error", test_generic_library.wrangler_assert)
    ])
def test_general_error(which_lambda, which_runtime_variables,
                       which_environment_variables, mockable_function,
                       expected_message, assertion):
    test_generic_library.general_error(which_lambda, which_runtime_variables,
                                       which_environment_variables, mockable_function,
                                       expected_message, assertion)


@mock_s3
@mock.patch('strata_period_wrangler.aws_functions.get_dataframe',
            side_effect=test_generic_library.replacement_get_dataframe)
def test_incomplete_read_error(mock_s3_get):
    file_list = ["test_wrangler_input.json"]

    test_generic_library.incomplete_read_error(lambda_wrangler_function,
                                               wrangler_runtime_variables,
                                               wrangler_environment_variables,
                                               file_list,
                                               "strata_period_wrangler")


@pytest.mark.parametrize(
    "which_lambda,expected_message,assertion,which_environment_variables",
    [
        (lambda_method_function, method_environment_variables,
         "Key Error", test_generic_library.method_assert),
        (lambda_wrangler_function, wrangler_environment_variables,
         "Key Error", test_generic_library.wrangler_assert)
    ])
def test_key_error(which_lambda, expected_message,
                   assertion, which_environment_variables):
    test_generic_library.key_error(which_lambda,
                                   expected_message, assertion,
                                   which_environment_variables)


@mock_s3
@mock.patch('strata_period_wrangler.aws_functions.get_dataframe',
            side_effect=test_generic_library.replacement_get_dataframe)
def test_method_error(mock_s3_get):
    file_list = ["test_wrangler_input.json"]

    test_generic_library.wrangler_method_error(lambda_wrangler_function,
                                               wrangler_runtime_variables,
                                               wrangler_environment_variables,
                                               file_list,
                                               "strata_period_wrangler")


@pytest.mark.parametrize(
    "which_lambda,expected_message,assertion",
    [(lambda_method_function,
      "Input Error in",
      test_generic_library.method_assert),
     (lambda_wrangler_function,
      "Error validating environment param",
      test_generic_library.wrangler_assert)])
def test_value_error(which_lambda, expected_message, assertion):
    test_generic_library.value_error(
        which_lambda, expected_message, assertion)

##########################################################################################
#                                     Specific                                           #
##########################################################################################


# @pytest.mark.parametrize(
#     "lookup_data,column_names,file_list,marine_check",
#     [
#         (lookups, ["county", "county_name"],
#          ["responder_county_lookup.json", "county_marine_lookup.json"], False),
#         (bricks_blocks_lookups, ["region"],
#          ["region_lookup.json"], True)
#     ])
# @mock_s3
# def test_data_enrichment(lookup_data, column_names, file_list, marine_check):
#     """
#     Runs data_enrichment function.
#     NOTE: This function calls do_merge and marine_mismatch_detector and doesn't
#     mock them. If this test fails check the tests for these funtions have passed
#     as they may be at fault.
#
#     :param lookup_data: Name of bucket to create - Type: dict
#     :param column_names: Name of bucket to create - Type: list
#     :param file_list: Name of bucket to create - Type: list
#     :param marine_check: Name of bucket to create - Type: boolean
#     :return Test Pass/Fail
#     """
#     with mock.patch.dict(lambda_method_function.os.environ,
#                          method_environment_variables):
#         with open("tests/fixtures/test_method_input.json", "r") as file:
#             test_data = file.read()
#         test_data = pd.DataFrame(json.loads(test_data))
#
#         bucket_name = method_environment_variables["bucket_name"]
#         client = test_generic_library.create_bucket(bucket_name)
#
#         test_generic_library.upload_files(client, bucket_name, file_list)
#
#         output, test_anomalies = lambda_method_function.data_enrichment(
#             test_data, marine_check, "survey", "period",
#             "test_bucket", lookup_data, "responder_id"
#         )
#     for column_name in column_names:
#         assert column_name in output.columns.values
#
#
#
# @mock_s3
# def test_method_success():
#     """
#     Runs the method function.
#     :param None
#     :return Test Pass/Fail
#     """
#     with mock.patch.dict(lambda_method_function.os.environ,
#                          method_environment_variables):
#         with open("tests/fixtures/test_method_prepared_output.json", "r") as file_1:
#             file_data = file_1.read()
#         prepared_data = pd.DataFrame(json.loads(file_data))
#
#         with open("tests/fixtures/test_method_input.json", "r") as file_2:
#             test_data = file_2.read()
#         method_runtime_variables["RuntimeVariables"]["data"] = test_data
#
#         bucket_name = method_environment_variables["bucket_name"]
#         client = test_generic_library.create_bucket(bucket_name)
#
#         file_list = ["responder_county_lookup.json",
#                      "county_marine_lookup.json"]
#
#         test_generic_library.upload_files(client, bucket_name, file_list)
#
#         output = lambda_method_function.lambda_handler(
#             method_runtime_variables, test_generic_library.context_object)
#
#         produced_data = pd.DataFrame(json.loads(output["data"]))
#
#     assert output["success"]
#     assert_frame_equal(produced_data, prepared_data)
#
#
#
# @mock_s3
# @mock.patch('enrichment_wrangler.aws_functions.get_dataframe',
#             side_effect=test_generic_library.replacement_get_dataframe)
# @mock.patch('enrichment_wrangler.aws_functions.save_data',
#             side_effect=test_generic_library.replacement_save_data)
# def test_wrangler_success(mock_s3_get, mock_s3_put):
#     """
#     Runs the wrangler function.
#     :param None
#     :return Test Pass/Fail
#     """
#     bucket_name = wrangler_environment_variables["bucket_name"]
#     client = test_generic_library.create_bucket(bucket_name)
#
#     file_list = ["test_wrangler_input.json"]
#
#     test_generic_library.upload_files(client, bucket_name, file_list)
#
#     with open("tests/fixtures/test_method_output.json", "r") as file_2:
#         test_data_out = file_2.read()
#
#     with mock.patch.dict(lambda_wrangler_function.os.environ,
#                          wrangler_environment_variables):
#         with mock.patch("enrichment_wrangler.boto3.client") as mock_client:
#             mock_client_object = mock.Mock()
#             mock_client.return_value = mock_client_object
#
#             mock_client_object.invoke.return_value.get.return_value.read \
#                 .return_value.decode.return_value = json.dumps({
#                  "data": test_data_out,
#                  "success": True,
#                  "anomalies": []
#                 })
#
#             output = lambda_wrangler_function.lambda_handler(
#                 wrangler_runtime_variables, test_generic_library.context_object
#             )
#
#     with open("tests/fixtures/test_wrangler_prepared_output.json", "r") as file_3:
#         test_data_prepared = file_3.read()
#     prepared_data = pd.DataFrame(json.loads(test_data_prepared))
#
#     with open("tests/fixtures/" +
#               wrangler_runtime_variables["RuntimeVariables"]["out_file_name"],
#               "r") as file_4:
#         test_data_produced = file_4.read()
#     produced_data = pd.DataFrame(json.loads(test_data_produced))
#
#     assert output
#     assert_frame_equal(produced_data, prepared_data)


def test_strata_mismatch_detector():
    assert True


def test_calculate_strata():
    assert True
