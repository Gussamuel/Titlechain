import uuid
from datetime import datetime

def transfer_mock_data(select_conn, title_conn):
    sel_cur = select_conn.cursor()
    tc_cur = title_conn.cursor()
    now = datetime.now()

    # helper to ask "does this already exist?"
    def exists_in_titlechain(table, where_clause, params):
        chk = title_conn.cursor()
        chk.execute(f"SELECT 1 FROM {table} WHERE {where_clause}", params)
        found = chk.fetchone() is not None
        chk.close()
        return found

    # ─── COPY ZREF LOOKUPS ──────────────────────────────────────────
    print("DEBUG: [Extractor] syncing zref lookup tables…")
    for schema, tbl in [
        ('zref', 'Easement'),
        ('zref', 'Exception1099'),
        ('zref', 'RequirementExceptionNumberingType'),
        ('zref', 'RequirementExceptionType'),
    ]:
        try:
            sel_cur.execute(f"SELECT [ID], [Description] FROM {schema}.{tbl}")
            for id_, desc in sel_cur.fetchall():
                if exists_in_titlechain(f"[{schema}].[{tbl}]", "ID = ?", (id_,)):
                    print(f"DEBUG: ⏭️ Skipping {schema}.{tbl}({id_}) — already synced")
                else:
                    tc_cur.execute(
                        f"INSERT INTO [{schema}].[{tbl}](ID, Description) VALUES (?, ?)",
                        (id_, desc)
                    )
                    print(f"DEBUG: ✅ Inserted {schema}.{tbl}({id_})")
        except Exception as e:
            print(f"DEBUG: [Extractor] skipping lookup {schema}.{tbl}: {e}")

    title_conn.commit()
    print("DEBUG: [Extractor] zref lookup sync complete")

    # ─── FETCH ALL PARCELS ─────────────────────────────────────────
    sel_cur.execute("""
        SELECT [RootId#], [Id#], [Type#]
          FROM pfm.Parcel
    """)
    parcels = sel_cur.fetchall()
    if not parcels:
        raise Exception("No parcels found in SelectDb.")

    for root_id, sp_parcel_id, sp_parcel_type in parcels:
        # ─── PROPERTIES ─────────────────────────────────────────────
        if exists_in_titlechain(
            "dbo.Properties",
            "SoftProRootId = ? AND SoftProParcelId = ?",
            (root_id, sp_parcel_id)
        ):
            fetch = title_conn.cursor()
            fetch.execute(
                "SELECT PropertyID FROM dbo.Properties WHERE SoftProRootId = ? AND SoftProParcelId = ?",
                (root_id, sp_parcel_id)
            )
            prop_guid = fetch.fetchone()[0]
            fetch.close()
            print(f"DEBUG: ⏭️ Skipping Properties({root_id},{sp_parcel_id}) → {prop_guid}")
        else:
            prop_guid = str(uuid.uuid4())
            tc_cur.execute(
                """
                INSERT INTO dbo.Properties
                  (PropertyID, SoftProParcelId, SoftProRootId, ParcelNumber, ParcelType, CreatedOn)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (prop_guid, sp_parcel_id, root_id, str(sp_parcel_id), sp_parcel_type, now)
            )
            print(f"DEBUG: ✅ Inserted Properties(PropertyID={prop_guid})")

        # ─── OWNERS ─────────────────────────────────────────────────
        sel_cur.execute(
            """
            SELECT [Id#] FROM pfm.Grantor WHERE [RootId#] = ?
            """,
            (root_id,)
        )
        for (sp_grantor_id,) in sel_cur.fetchall():
            if exists_in_titlechain(
                "dbo.Owners",
                "SoftProGrantorId = ? AND PropertyID = ?",
                (sp_grantor_id, prop_guid)
            ):
                print(f"DEBUG: ⏭️ Skipping Owners(Grantor={sp_grantor_id})")
            else:
                owner_guid = str(uuid.uuid4())
                tc_cur.execute(
                    """
                    INSERT INTO dbo.Owners
                      (OwnerID, PropertyID, SoftProGrantorId, Name, Address, CreatedOn)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (owner_guid, prop_guid, sp_grantor_id, None, None, now)
                )
                print(f"DEBUG: ✅ Inserted Owners(OwnerID={owner_guid})")

        # ─── POLICIES ───────────────────────────────────────────────
        sel_cur.execute(
            """
            SELECT [Id#] FROM pfm.Policy WHERE [RootId#] = ?
            """,
            (root_id,)
        )
        for (sp_policy_id,) in sel_cur.fetchall():
            if exists_in_titlechain(
                "dbo.Policies",
                "SoftProPolicyId = ? AND PropertyID = ?",
                (sp_policy_id, prop_guid)
            ):
                print(f"DEBUG: ⏭️ Skipping Policies(Policy={sp_policy_id})")
            else:
                policy_guid = str(uuid.uuid4())
                tc_cur.execute(
                    """
                    INSERT INTO dbo.Policies
                      (PolicyID, PropertyID, SoftProPolicyId, PolicyNumber, PolicyDate,
                       CoverageAmount, PolicyType, CreatedOn)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (policy_guid, prop_guid, sp_policy_id, None, None, None, None, now)
                )
                print(f"DEBUG: ✅ Inserted Policies(PolicyID={policy_guid})")

        # ─── DOCUMENTS ──────────────────────────────────────────────
        for schema, tbl in [('dbo','zrefDocReportType'), ('zref','DocReportType')]:
            try:
                sel_cur.execute(f"SELECT [ID], [Description] FROM {schema}.{tbl}")
                for dt_id, dt_desc in sel_cur.fetchall():
                    if exists_in_titlechain(
                        "dbo.Documents",
                        "SoftProDocId = ? AND PropertyID = ?",
                        (dt_id, prop_guid)
                    ):
                        print(f"DEBUG: ⏭️ Skipping Documents(SoftProDocId={dt_id})")
                    else:
                        doc_guid = str(uuid.uuid4())
                        tc_cur.execute(
                            """
                            INSERT INTO dbo.Documents
                              (DocumentID, PropertyID, SoftProDocId, FileName, FilePath, DocType, CreatedOn)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                            """,
                            (doc_guid, prop_guid, dt_id, None, None, dt_desc, now)
                        )
                        print(f"DEBUG: ✅ Inserted Documents(DocumentID={doc_guid})")
                break
            except Exception as e:
                print(f"DEBUG: [Extractor] skipping {schema}.{tbl}: {e}")

        # ─── EASEMENTS ───────────────────────────────────────────────
        try:
            sel_cur.execute("SELECT [Id#] FROM pfm.Easement WHERE [RootId#] = ?", (root_id,))
            for (sp_easement_id,) in sel_cur.fetchall():
                if exists_in_titlechain(
                    "dbo.Easements",
                    "SoftProEasementId = ? AND PropertyID = ?",
                    (sp_easement_id, prop_guid)
                ):
                    print(f"DEBUG: ⏭️ Skipping Easements(SoftProEasementId={sp_easement_id})")
                else:
                    ease_guid = str(uuid.uuid4())
                    tc_cur.execute(
                        """
                        INSERT INTO dbo.Easements
                          (EasementID, PropertyID, SoftProEasementId, Code, Description, CreatedOn)
                        VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (ease_guid, prop_guid, sp_easement_id, None, None, now)
                    )
                    print(f"DEBUG: ✅ Inserted Easements(EasementID={ease_guid})")
        except Exception as e:
            print(f"DEBUG: [Extractor] skipping Easements: {e}")

        # ─── POLICY EXCEPTIONS ───────────────────────────────────────
        try:
            sel_cur.execute("SELECT [Id#] FROM pfm.Exception1099 WHERE [RootId#] = ?", (root_id,))
            for (sp_exc_id,) in sel_cur.fetchall():
                if exists_in_titlechain(
                    "dbo.PolicyExceptions",
                    "SoftProExceptionId = ? AND PropertyID = ?",
                    (sp_exc_id, prop_guid)
                ):
                    print(f"DEBUG: ⏭️ Skipping PolicyExceptions(SoftProExceptionId={sp_exc_id})")
                else:
                    exc_guid = str(uuid.uuid4())
                    tc_cur.execute(
                        """
                        INSERT INTO dbo.PolicyExceptions
                          (ExceptionID, PropertyID, SoftProExceptionId, ExceptionCode, Description, CreatedOn)
                        VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (exc_guid, prop_guid, sp_exc_id, None, None, now)
                    )
                    print(f"DEBUG: ✅ Inserted PolicyExceptions(ExceptionID={exc_guid})")
        except Exception as e:
            print(f"DEBUG: [Extractor] skipping PolicyExceptions: {e}")

        # ─── REQUIREMENTS ───────────────────────────────────────────
        try:
            sel_cur.execute("SELECT [Id#] FROM pfm.RequirementExceptionType WHERE [RootId#] = ?", (root_id,))
            for (sp_req_id,) in sel_cur.fetchall():
                if exists_in_titlechain(
                    "dbo.Requirements",
                    "SoftProReqId = ? AND PropertyID = ?",
                    (sp_req_id, prop_guid)
                ):
                    print(f"DEBUG: ⏭️ Skipping Requirements(SoftProReqId={sp_req_id})")
                else:
                    req_guid = str(uuid.uuid4())
                    tc_cur.execute(
                        """
                        INSERT INTO dbo.Requirements
                          (RequirementID, PropertyID, SoftProReqId, ReqTypeCode, ReqTypeDesc,
                           NumberingTypeCode, NumberingTypeDesc, CreatedOn)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (req_guid, prop_guid, sp_req_id, None, None, None, None, now)
                    )
                    print(f"DEBUG: ✅ Inserted Requirements(RequirementID={req_guid})")
        except Exception as e:
            print(f"DEBUG: [Extractor] skipping Requirements: {e}")

    title_conn.commit()
    print("DEBUG: [Extractor] Committed all changes; exiting")
    sel_cur.close()
    tc_cur.close()