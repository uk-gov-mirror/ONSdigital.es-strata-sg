import logging
import os

import marshmallow
import pandas as pd


class EnvironSchema(marshmallow.Schema):
    """
    Class to set up the environment variables schema.
    """
    strata_column = marshmallow.fields.Str(required=True)
    value_column = marshmallow.fields.Str(required=True)


def lambda_handler(event, context):
    """
    Applies Calculate strata function to row of DataFrame.
    :param event: Event Object.
    :param context: Context object.
    :return: strata_out - Dict with "success" and "data" or "success and "error".
    """
    current_module = "Strata - Method"
    error_message = ""
    log_message = ""
    logger = logging.getLogger("Strata")
    try:

        logger.info("Strata Method Begun")

        schema = EnvironSchema()
        config, errors = schema.load(os.environ)
        if errors:
            raise ValueError(f"Error validating environment parameters: {errors}")

        logger.info("Vaildated params")

        data = event['RuntimeVariables']["data"]
        survey_column = event['RuntimeVariables']["survey_column"]
        region_column = event['RuntimeVariables']["region_column"]

        logger.info("Succesfully retrieved data from event")

        strata_column = config["strata_column"]
        value_column = config["value_column"]

        input_data = pd.read_json(data, dtype=False)
        post_strata = input_data.apply(
            calculate_strata,
            strata_column=strata_column,
            value_column=value_column,
            survey_column=survey_column,
            region_column=region_column,
            axis=1,
        )
        logger.info("Successfully ran calculation")
        json_out = post_strata.to_json(orient="records")

        final_output = {"data": json_out}

    except ValueError as e:
        error_message = (
            "Input Error in "
            + current_module
            + " |- "
            + str(e.args)
            + " | Request ID: "
            + str(context.aws_request_id)
        )
        log_message = error_message + " | Line: " + str(e.__traceback__.tb_lineno)
    except KeyError as e:
        error_message = (
            "Key Error in "
            + current_module
            + " |- "
            + str(e.args)
            + " | Request ID: "
            + str(context.aws_request_id)
        )
        log_message = error_message + " | Line: " + str(e.__traceback__.tb_lineno)
    except Exception as e:
        error_message = (
            "General Error in "
            + current_module
            + " ("
            + str(type(e))
            + ") |- "
            + str(e.args)
            + " | Request ID: "
            + str(context.aws_request_id)
        )
        log_message = error_message + " | Line: " + str(e.__traceback__.tb_lineno)
    finally:
        if (len(error_message)) > 0:
            logger.error(log_message)
            return {"success": False, "error": error_message}

    logger.info("Successfully completed module: " + current_module)
    final_output['success'] = True
    return final_output


def calculate_strata(row, value_column, region_column, strata_column, survey_column):
    """
    Calculates the strata for the reference based on Land or Marine value, question total
    value and region.
    :param row: Row of the dataframe that is being passed into the function.
    :param value_column: Column of the dataframe containing the Q608 total.
    :param region_column: Column name of the dataframe containing the region code.
    :param strata_column: Column of dataframe for the strata_column to be held.
    :param survey_column: Column name of the dataframe containing the survey code.
    :return: row: The calculated row including the strata.
    """
    row[strata_column] = ""

    if not row[value_column]:
        return row

    if row[strata_column] == "":
        if row[survey_column] == "076":
            row[strata_column] = "M"
        if row[survey_column] == "066" and row[value_column] < 30000:
            row[strata_column] = "E"
        if row[survey_column] == "066" and row[value_column] > 29999:
            row[strata_column] = "D"
        if row[survey_column] == "066" and row[value_column] > 79999:
            row[strata_column] = "C"
        if (
            row[survey_column] == "066"
            and row[value_column] > 129999
            and row[region_column] > 9
        ):
            row[strata_column] = "B2"
        if (
            row[survey_column] == "066"
            and row[value_column] > 129999
            and row[region_column] < 10
        ):
            row[strata_column] = "B1"
        if row[survey_column] == "066" and row[value_column] > 200000:
            row[strata_column] = "A"
    return row
